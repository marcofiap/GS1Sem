####################################
##### Arquivo: app.py
##### Desenvolvedor: Juan F. Voltolini
##### Instituição: FIAP
##### Trabalho: Global Solution - 1º Semestre
##### Grupo: Felipe Sabino da Silva, Juan Felipe Voltolini, Luiz Henrique Ribeiro de Oliveira, Marco Aurélio Eberhardt Assumpção e Paulo Henrique Senise
####################################

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys
import os
from pathlib import Path
import numpy as np
import base64
from io import BytesIO

# Adicionar o diretório src ao path para importações
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.api.controller import get_controller
from src.utils.logging import setup_logging, get_logger
from src.r_analysis import RAnalyzer

# Configurar logging
setup_logging()
logger = get_logger(__name__)

# Configuração da página
st.set_page_config(
    page_title="Sistema de Monitoramento de Qualidade da Água",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .alert-high {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
        padding: 10px;
        border-radius: 5px;
    }
    .alert-medium {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
        padding: 10px;
        border-radius: 5px;
    }
    .status-potable {
        color: #4caf50;
        font-weight: bold;
    }
    .status-not-potable {
        color: #f44336;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=60)  # Cache por 60 segundos
def get_system_statistics():
    """Recupera estatísticas do sistema com cache."""
    try:
        controller = get_controller()
        return controller.get_statistics()
    except Exception as e:
        logger.error(f"Erro ao carregar estatísticas: {e}")
        return {}


@st.cache_data(ttl=30)  # Cache por 30 segundos
def get_recent_readings(limit=100):
    """Recupera leituras recentes com cache."""
    try:
        controller = get_controller()
        return controller.get_readings(limit)
    except Exception as e:
        logger.error(f"Erro ao carregar leituras: {e}")
        return []


@st.cache_data(ttl=30)  # Cache por 30 segundos
def get_recent_alerts():
    """Recupera alertas recentes com cache."""
    try:
        controller = get_controller()
        return controller.get_alerts()
    except Exception as e:
        logger.error(f"Erro ao carregar alertas: {e}")
        return []


def main():
    st.title("💧 Sistema de Monitoramento de Qualidade da Água")
    st.markdown("**Monitoramento em tempo real da potabilidade da água usando IoT e Machine Learning**")

    # Sidebar
    st.sidebar.title("Navegação")
    page = st.sidebar.selectbox(
        "Escolha uma página:",
        ["Dashboard", "Análise Detalhada", "Dataset", "Histórico", "Alertas", "Configurações", "Análise em R"]
    )

    if page == "Dashboard":
        show_dashboard()
    elif page == "Análise Detalhada":
        show_detailed_analysis()
    elif page == "Dataset":
        show_dataset()
    elif page == "Histórico":
        show_history()
    elif page == "Alertas":
        show_alerts()
    elif page == "Configurações":
        show_settings()
    elif page == "Análise em R":
        show_r_analysis()


def show_dashboard():
    """Exibe dashboard principal."""
    st.header("📊 Dashboard Principal")

    # Carregar dados
    stats = get_system_statistics()

    if not stats or 'error' in stats:
        st.error("❌ Erro ao carregar dados do sistema. Verifique a conexão com o banco de dados.")
        return

    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total de Leituras", stats.get('total_readings', 0))

    with col2:
        potable_pct = stats.get('potable_percentage', 0)
        st.metric("Água Potável (%)", f"{potable_pct:.1f}%")

    with col3:
        st.metric("Alertas Ativos", stats.get('alerts_count', 0))

    with col4:
        if stats.get('last_reading'):
            last_time = datetime.fromisoformat(stats['last_reading']['timestamp'].replace('Z', '+00:00'))
            minutes_ago = int((datetime.now() - last_time.replace(tzinfo=None)).total_seconds() / 60)
            st.metric("Última Leitura", f"{minutes_ago} min atrás")
        else:
            st.metric("Última Leitura", "N/A")

    # Status atual
    st.subheader("📍 Status Atual do Sistema")

    if stats.get('last_reading'):
        last_reading = stats['last_reading']
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(f"""
            **Última Leitura:** {last_reading['timestamp']}

            **Parâmetros:**
            - pH: {last_reading['ph']:.2f}
            - Turbidez: {last_reading['turbidity']:.2f} NTU
            - Cloraminas: {last_reading['chloramines']:.2f} ppm
            """)

        with col2:
            if last_reading['potability'] == 1:
                st.success("✅ Água POTÁVEL")
            else:
                st.error("⚠️ Água NÃO POTÁVEL")

    # Gráficos
    st.subheader("📈 Tendências Recentes")

    readings = get_recent_readings(50)  # Últimas 50 leituras

    if readings:
        df = pd.DataFrame(readings)
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%dT%H:%M:%S.%f')

        # Gráfico de pH ao longo do tempo
        col1, col2 = st.columns(2)

        with col1:
            fig_ph = px.line(df, x='timestamp', y='ph', title='pH ao Longo do Tempo')
            fig_ph.add_hline(y=6.5, line_dash="dash", line_color="red", annotation_text="pH Mín")
            fig_ph.add_hline(y=8.5, line_dash="dash", line_color="red", annotation_text="pH Máx")
            st.plotly_chart(fig_ph, use_container_width=True)

        with col2:
            fig_turb = px.line(df, x='timestamp', y='turbidity', title='Turbidez ao Longo do Tempo')
            fig_turb.add_hline(y=5, line_dash="dash", line_color="orange", annotation_text="Limite Ideal")
            st.plotly_chart(fig_turb, use_container_width=True)

        # Distribuição de potabilidade
        potability_counts = df['potability_label'].value_counts()
        fig_pie = px.pie(values=potability_counts.values, names=potability_counts.index,
                         title='Distribuição de Potabilidade')
        st.plotly_chart(fig_pie, use_container_width=True)


def show_detailed_analysis():
    """Exibe análise detalhada."""
    st.header("🔬 Análise Detalhada")

    st.markdown("Insira valores dos sensores para análise detalhada da qualidade da água:")

    # Formulário para entrada de dados
    with st.form("analysis_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            ph = st.number_input("pH", min_value=0.0, max_value=14.0, value=7.0, step=0.1)

        with col2:
            turbidity = st.number_input("Turbidez (NTU)", min_value=0.0, value=4.0, step=0.1)

        with col3:
            chloramines = st.number_input("Cloraminas (ppm)", min_value=0.0, value=1.0, step=0.1)

        submitted = st.form_submit_button("Analisar")

    if submitted:
        try:
            controller = get_controller()

            sensor_data = {
                'ph': ph,
                'turbidity': turbidity,
                'chloramines': chloramines
            }

            # Fazer análise detalhada
            evaluation = controller.evaluate_water_quality_detailed(sensor_data)

            if 'error' in evaluation:
                st.error(f"Erro na análise: {evaluation['error']}")
                return

            # Exibir resultados
            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader("📊 Resultado da Análise")

                # Status geral
                if evaluation['is_potable']:
                    st.success("✅ Água POTÁVEL")
                else:
                    st.error("⚠️ Água NÃO POTÁVEL")

                # Nível de confiança
                confidence = evaluation['confidence'] * 100
                st.metric("Confiança da Predição", f"{confidence:.1f}%")

                # Probabilidades
                prob_potable = evaluation['probabilities']['potable'] * 100
                prob_not_potable = evaluation['probabilities']['not_potable'] * 100

                st.markdown("**Probabilidades:**")
                st.markdown(f"- Potável: {prob_potable:.1f}%")
                st.markdown(f"- Não Potável: {prob_not_potable:.1f}%")

            with col2:
                # Nível de risco
                risk_level = evaluation['risk_level']
                risk_colors = {
                    'muito_baixo': 'green',
                    'baixo': 'lightgreen',
                    'medio': 'orange',
                    'alto': 'red'
                }

                st.markdown(
                    f"**Nível de Risco:** <span style='color: {risk_colors.get(risk_level, 'gray')}'>{risk_level.replace('_', ' ').title()}</span>",
                    unsafe_allow_html=True)

            # Análise de parâmetros
            st.subheader("🔍 Análise de Parâmetros")

            for param, analysis in evaluation['parameter_analysis'].items():
                col1, col2, col3 = st.columns([1, 1, 2])

                with col1:
                    st.metric(param.title(), f"{analysis['value']:.2f}")

                with col2:
                    status = analysis['status']
                    if status == 'normal':
                        st.success("Normal")
                    elif status == 'atencao':
                        st.warning("Atenção")
                    else:
                        st.error("Crítico")

                with col3:
                    st.text(f"Faixa ideal: {analysis['ideal_range']}")

            # Recomendações
            st.subheader("💡 Recomendações")
            for rec in evaluation['recommendations']:
                st.markdown(f"- {rec}")

        except Exception as e:
            st.error(f"Erro na análise: {e}")
            logger.error(f"Erro na análise detalhada: {e}")


def show_history():
    """Exibe histórico de leituras."""
    st.header("📚 Histórico de Leituras")

    # Opções de filtro
    col1, col2 = st.columns(2)

    with col1:
        limit = st.selectbox("Número de leituras:", [50, 100, 200, 500, 1000], index=1)

    with col2:
        show_only_alerts = st.checkbox("Mostrar apenas alertas")

    # Carregar dados
    if show_only_alerts:
        readings = get_recent_alerts()
    else:
        readings = get_recent_readings(limit)

    if not readings:
        st.warning("Nenhuma leitura encontrada.")
        return

    # Converter para DataFrame
    df = pd.DataFrame(readings)
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%dT%H:%M:%S.%f')

    # Estatísticas rápidas
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total de Registros", len(df))

    with col2:
        if 'potability' in df.columns:
            potable_count = (df['potability'] == 1).sum()
            st.metric("Água Potável", potable_count)

    with col3:
        if 'potability' in df.columns:
            not_potable_count = (df['potability'] == 0).sum()
            st.metric("Água Não Potável", not_potable_count)

    # Tabela de dados
    st.subheader("📋 Dados Detalhados")

    # Preparar dados para exibição
    display_df = df.copy()
    display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

    if 'potability_label' in display_df.columns:
        display_df['Status'] = display_df['potability_label'].map({
            'POTAVEL': '✅ Potável',
            'NAO_POTAVEL': '⚠️ Não Potável'
        })

    # Renomear colunas para exibição
    column_names = {
        'timestamp': 'Data/Hora',
        'ph': 'pH',
        'turbidity': 'Turbidez (NTU)',
        'chloramines': 'Cloraminas (ppm)',
        'Status': 'Status'
    }

    display_columns = ['timestamp', 'ph', 'turbidity', 'chloramines']
    if 'Status' in display_df.columns:
        display_columns.append('Status')

    st.dataframe(
        display_df[display_columns].rename(columns=column_names),
        use_container_width=True
    )

    # Opção de download
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Baixar dados em CSV",
        data=csv,
        file_name=f"water_quality_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )


def show_alerts():
    """Exibe alertas ativos."""
    st.header("🚨 Alertas e Notificações")

    alerts = get_recent_alerts()

    if not alerts:
        st.success("✅ Nenhum alerta ativo no momento!")
        return

    st.warning(f"⚠️ {len(alerts)} alerta(s) ativo(s)")

    for alert in alerts:
        severity = alert.get('severity', 'media')

        if severity == 'critica':
            alert_class = 'alert-high'
            icon = '🔴'
        elif severity == 'alta':
            alert_class = 'alert-high'
            icon = '🟠'
        else:
            alert_class = 'alert-medium'
            icon = '🟡'

        st.markdown(f"""
        <div class="{alert_class}">
            <h4>{icon} Alerta - Severidade: {severity.title()}</h4>
            <p><strong>Data/Hora:</strong> {alert['timestamp']}</p>
            <p><strong>Descrição:</strong> {alert['message']}</p>
            <p><strong>Parâmetros:</strong> pH={alert['ph']:.2f}, Turbidez={alert['turbidity']:.2f}, Cloraminas={alert['chloramines']:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")


def show_settings():
    """Exibe configurações do sistema."""
    st.header("⚙️ Configurações do Sistema")

    st.subheader("🔄 Atualização de Dados")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Atualizar Cache"):
            st.cache_data.clear()
            st.success("Cache limpo com sucesso!")

    with col2:
        if st.button("📊 Recarregar Estatísticas"):
            st.rerun()

    st.subheader("🎛️ Parâmetros de Qualidade")

    st.markdown("""
    **Faixas de Referência para Qualidade da Água:**

    - **pH:** 6.5 - 8.5 (ideal)
    - **Turbidez:** < 5 NTU (ideal)
    - **Cloraminas:** 0.2 - 2.0 ppm (ideal)
    """)

    st.subheader("ℹ️ Informações do Sistema")

    st.markdown("""
    **Sistema de Monitoramento de Qualidade da Água**

    - **Versão:** 1.0.0
    - **Desenvolvido por:** Felipe Sabino da Silva, Juan Felipe Voltolini, Luiz Henrique Ribeiro de Oliveira, Marco Aurélio Eberhardt Assumpção e Paulo Henrique Senise
    - **Instituição:** FIAP
    - **Projeto:** Global Solution - 1º Semestre

    **Tecnologias Utilizadas:**
    - Python + Streamlit (Interface)
    - Scikit-learn (Machine Learning)
    - Oracle Database (Persistência)
    - ESP32 + Sensores (IoT)
    """)


def show_dataset():
    """Exibe informações sobre o dataset de treinamento."""
    st.header("📊 Dataset de Treinamento")

    try:
        # Carregar dataset
        dataset_path = Path(__file__).parent.parent.parent / "water_potability.csv"

        if not dataset_path.exists():
            st.error("❌ Dataset não encontrado!")
            return

        df = pd.read_csv(dataset_path)

        # Informações básicas
        st.subheader("ℹ️ Informações Básicas")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total de Registros", len(df))

        with col2:
            missing_values = df.isnull().sum().sum()
            st.metric("Valores Ausentes", missing_values)

        with col3:
            potable_count = df['Potability'].sum()
            st.metric("Água Potável", potable_count)

        with col4:
            non_potable = len(df) - potable_count
            st.metric("Água Não Potável", non_potable)

        # Distribuição da variável target
        st.subheader("🎯 Distribuição da Variável Target")

        col1, col2 = st.columns([1, 1])

        with col1:
            potability_counts = df['Potability'].value_counts()
            fig_pie = px.pie(
                values=potability_counts.values,
                names=['Não Potável', 'Potável'],
                title='Distribuição de Potabilidade',
                color_discrete_sequence=['#ff6b6b', '#51cf66']
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            st.markdown(f"""
            **Estatísticas da Variável Target:**

            - **Água Potável:** {potable_count} ({potable_count / len(df) * 100:.1f}%)
            - **Água Não Potável:** {non_potable} ({non_potable / len(df) * 100:.1f}%)
            - **Balanceamento:** {'Desbalanceado' if abs(potable_count - non_potable) > len(df) * 0.1 else 'Balanceado'}

            **Observações:**
            - Dataset com {len(df)} amostras
            - {df.shape[1]} features + 1 target
            - {missing_values} valores ausentes no total
            """)

        # Estatísticas das features
        st.subheader("📈 Estatísticas das Features")

        # Preparar dados para estatísticas
        feature_columns = ['ph', 'Hardness', 'Solids', 'Chloramines', 'Sulfate',
                           'Conductivity', 'Organic_carbon', 'Trihalomethanes', 'Turbidity']

        stats_data = []
        for col in feature_columns:
            if col in df.columns:
                stats_data.append({
                    'Feature': col,
                    'Média': f"{df[col].mean():.2f}",
                    'Mediana': f"{df[col].median():.2f}",
                    'Desvio Padrão': f"{df[col].std():.2f}",
                    'Mínimo': f"{df[col].min():.2f}",
                    'Máximo': f"{df[col].max():.2f}",
                    'Valores Ausentes': df[col].isnull().sum()
                })

        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True)

        # Visualizações das features
        st.subheader("📊 Distribuições das Features")

        # Selecionar features para visualizar
        selected_features = st.multiselect(
            "Selecione features para visualizar:",
            feature_columns,
            default=['ph', 'Turbidity', 'Chloramines'][:3]
        )

        if selected_features:
            # Criar histogramas
            for feature in selected_features:
                if feature in df.columns:
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        # Histograma por potabilidade
                        fig = px.histogram(
                            df,
                            x=feature,
                            color='Potability',
                            nbins=30,
                            title=f'Distribuição de {feature} por Potabilidade',
                            color_discrete_map={0: '#ff6b6b', 1: '#51cf66'},
                            labels={'Potability': 'Potabilidade'}
                        )
                        fig.update_layout(barmode='overlay')
                        fig.update_traces(opacity=0.7)
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        # Box plot
                        fig_box = px.box(
                            df,
                            y=feature,
                            color='Potability',
                            title=f'Box Plot - {feature}',
                            color_discrete_map={0: '#ff6b6b', 1: '#51cf66'}
                        )
                        st.plotly_chart(fig_box, use_container_width=True)

        # Matriz de correlação
        st.subheader("🔗 Matriz de Correlação")

        # Calcular correlação apenas para colunas numéricas
        numeric_df = df[feature_columns + ['Potability']].select_dtypes(include=[np.number])
        correlation_matrix = numeric_df.corr()

        fig_corr = px.imshow(
            correlation_matrix,
            text_auto=True,
            aspect="auto",
            title="Matriz de Correlação entre Features",
            color_continuous_scale='RdBu_r'
        )
        st.plotly_chart(fig_corr, use_container_width=True)

        # Performance do modelo
        st.subheader("🎯 Performance do Modelo")

        # Verificar se existe modelo treinado
        model_path = Path(__file__).parent.parent.parent / "src/model/water_quality_model.pkl"

        if model_path.exists():
            try:
                import joblib
                model_data = joblib.load(model_path)

                if 'model' in model_data and hasattr(model_data['model'], 'feature_importances_'):
                    # Importância das features
                    feature_importance = model_data['model'].feature_importances_
                    feature_names = feature_columns

                    importance_df = pd.DataFrame({
                        'Feature': feature_names,
                        'Importância': feature_importance
                    }).sort_values('Importância', ascending=True)

                    fig_importance = px.bar(
                        importance_df,
                        x='Importância',
                        y='Feature',
                        orientation='h',
                        title='Importância das Features no Modelo Random Forest',
                        color='Importância',
                        color_continuous_scale='viridis'
                    )
                    st.plotly_chart(fig_importance, use_container_width=True)

                else:
                    st.warning("⚠️ Informações de importância não disponíveis no modelo")

            except Exception as e:
                st.error(f"❌ Erro ao carregar modelo: {e}")
        else:
            st.warning("⚠️ Modelo não encontrado. Execute `python train_model.py` primeiro.")

        # Amostra dos dados
        st.subheader("🔍 Amostra dos Dados")

        col1, col2 = st.columns(2)

        with col1:
            show_sample = st.checkbox("Mostrar amostra dos dados", value=False)

        with col2:
            sample_size = st.slider("Tamanho da amostra:", 5, 100, 20)

        if show_sample:
            sample_df = df.sample(n=min(sample_size, len(df)))
            st.dataframe(sample_df, use_container_width=True)

        # Download do dataset
        st.subheader("💾 Download")

        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Baixar Dataset Completo (CSV)",
            data=csv,
            file_name=f"water_potability_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"❌ Erro ao carregar dataset: {e}")
        logger.error(f"Erro no show_dataset: {e}")


def show_r_analysis():
    """Exibe página de análise estatística em R."""
    st.header("📊 Análise Estatística em R")
    
    st.markdown("""
    **Análises estatísticas avançadas usando R para dados de qualidade da água**
    
    Esta página permite realizar análises estatísticas detalhadas dos dados coletados pelos sensores,
    utilizando a linguagem R para processamento e visualização avançada.
    """)
    
    # Seleção do tipo de dados
    st.subheader("🗂️ Fonte dos Dados")
    
    data_source = st.radio(
        "Escolha a fonte dos dados para análise:",
        options=["Dados Pré-carregados", "Dados Coletados em Tempo Real"],
        help="Selecione se deseja analisar o dataset pré-carregado ou os dados coletados pelos sensores"
    )
    
    # Divisor visual
    st.divider()
    
    if data_source == "Dados Pré-carregados":
        show_preloaded_data_analysis()
    else:
        show_realtime_data_analysis()


def show_preloaded_data_analysis():
    """Exibe análise dos dados pré-carregados."""
    st.subheader("📈 Análise de Dados Pré-carregados")
    
    st.info("""
    **Dataset de Treinamento**
    
    Utilizando o dataset `water_potability.csv` com dados históricos para análises estatísticas.
    """)
    
    # Verificar se R está disponível
    r_analyzer = RAnalyzer()
    r_available = r_analyzer.check_r_availability()
    
    # Adicionar informações de debug
    with st.expander("🔧 Debug - Informações do Sistema"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Ambiente Python:**")
            st.code(f"""
Virtual Env: {os.environ.get('VIRTUAL_ENV', 'Não detectada')}
Python: {sys.executable}
Working Dir: {os.getcwd()}
            """)
        
        with col2:
            st.markdown("**Detecção do R:**")
            if r_available:
                st.success(f"✅ R encontrado em: {r_analyzer.rscript_path}")
            else:
                st.error("❌ R não encontrado")
                
            if st.button("🔄 Forçar Nova Detecção do R"):
                # Criar nova instância para forçar nova detecção
                st.cache_data.clear()  # Limpar cache do Streamlit
                r_analyzer = RAnalyzer()  # Nova instância
                r_available = r_analyzer.check_r_availability(force_recheck=True)
                if r_available:
                    st.success(f"✅ R encontrado após nova detecção: {r_analyzer.rscript_path}")
                    st.rerun()
                else:
                    st.error("❌ R ainda não foi encontrado")
    
    if not r_available:
        return
    
    # Carregar dataset
    try:
        dataset_path = Path(__file__).parent.parent.parent / "water_potability.csv"
        if not dataset_path.exists():
            st.error("❌ Dataset water_potability.csv não encontrado!")
            return
        
        df = pd.read_csv(dataset_path)
        
        # Informações sobre o dataset
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Registros", f"{len(df):,}")
        
        with col2:
            st.metric("Variáveis", f"{len(df.columns)}")
        
        with col3:
            missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            st.metric("% Valores Ausentes", f"{missing_pct:.1f}%")
        
        with col4:
            potable_pct = (df['Potability'].sum() / len(df)) * 100
            st.metric("% Potável", f"{potable_pct:.1f}%")
        
        # Seleção de variáveis para análise
        st.subheader("🔬 Configuração da Análise")
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        if 'Potability' in numeric_columns:
            numeric_columns.remove('Potability')
        
        selected_vars = st.multiselect(
            "Selecione as variáveis para análise:",
            options=numeric_columns,
            default=numeric_columns[:3] if len(numeric_columns) >= 3 else numeric_columns,
            help="Escolha quais variáveis numéricas analisar"
        )
        
        if not selected_vars:
            st.warning("⚠️ Selecione pelo menos uma variável para análise.")
            return
        
        # Tipos de análise
        analysis_types = st.multiselect(
            "Selecione os tipos de análise:",
            options=[
                "Medidas de Tendência Central",
                "Medidas de Dispersão", 
                "Medidas Separatrizes",
                "Gráficos (Histograma, Boxplot)",
                "Análise de Potabilidade"
            ],
            default=["Medidas de Tendência Central", "Gráficos (Histograma, Boxplot)"]
        )
        
        if st.button("🚀 Executar Análises Estatísticas em R", type="primary"):
            
            # Preparar dados para análise
            analysis_df = df[selected_vars + ['Potability']].copy()
            analysis_df = analysis_df.rename(columns={'Potability': 'potability'})
            
            with st.spinner("⏳ Executando análises estatísticas em R..."):
                
                try:
                    # Executar análise R
                    results = r_analyzer.analyze_data(analysis_df)
                    
                    if "error" in results:
                        st.error(f"❌ Erro na análise: {results['error']}")
                        return
                    
                    st.success("✅ Análises concluídas com sucesso!")
                    
                    # Exibir resultados estatísticos
                    if "statistics" in results and results["statistics"]:
                        st.subheader("📊 Resultados Estatísticos")
                        
                        for var, stats in results["statistics"].items():
                            st.markdown(f"### 📈 {var.title()}")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            # Tendência central
                            if "tendencia_central" in stats:
                                with col1:
                                    st.markdown("**Tendência Central**")
                                    tc = stats["tendencia_central"]
                                    st.metric("Média", f"{tc.get('media', 0):.4f}")
                                    st.metric("Mediana", f"{tc.get('mediana', 0):.4f}")
                                    st.metric("Moda", f"{tc.get('moda', 0):.4f}")
                            
                            # Dispersão
                            if "dispersao" in stats:
                                with col2:
                                    st.markdown("**Dispersão**")
                                    disp = stats["dispersao"]
                                    st.metric("Variância", f"{disp.get('variancia', 0):.4f}")
                                    st.metric("Desvio Padrão", f"{disp.get('desvio_padrao', 0):.4f}")
                                    st.metric("Amplitude", f"{disp.get('amplitude', 0):.4f}")
                                    st.metric("IQR", f"{disp.get('iqr', 0):.4f}")
                            
                            # Separatrizes
                            if "separatrizes" in stats:
                                with col3:
                                    st.markdown("**Separatrizes**")
                                    sep = stats["separatrizes"]
                                    
                                    if "quartis" in sep:
                                        quartis = sep["quartis"]
                                        # quartis vem como lista [Q1, Q2, Q3] do R
                                        if isinstance(quartis, list) and len(quartis) >= 3:
                                            st.metric("Q1", f"{quartis[0]:.4f}")
                                            st.metric("Q2 (Mediana)", f"{quartis[1]:.4f}")
                                            st.metric("Q3", f"{quartis[2]:.4f}")
                                        elif isinstance(quartis, dict):
                                            # Fallback para formato de dicionário
                                            st.metric("Q1", f"{quartis.get('25%', 0):.4f}")
                                            st.metric("Q2 (Mediana)", f"{quartis.get('50%', 0):.4f}")
                                            st.metric("Q3", f"{quartis.get('75%', 0):.4f}")
                            
                            st.divider()
                    
                    # Exibir gráficos
                    if "graphics" in results and results["graphics"]:
                        st.subheader("📊 Visualizações")
                        
                        # Organizar gráficos em colunas
                        graphics = results["graphics"]
                        
                        # Gráficos de barras para potabilidade
                        if "barplot_potability" in graphics:
                            st.markdown("### 📊 Distribuição de Potabilidade")
                            img_data = base64.b64decode(graphics["barplot_potability"])
                            st.image(img_data, use_column_width=True)
                            st.divider()
                        
                        # Histogramas e boxplots
                        for var in selected_vars:
                            hist_key = f"histogram_{var}"
                            box_key = f"boxplot_{var}"
                            
                            if hist_key in graphics or box_key in graphics:
                                st.markdown(f"### 📈 {var.title()}")
                                
                                col1, col2 = st.columns(2)
                                
                                if hist_key in graphics:
                                    with col1:
                                        st.markdown("**Histograma**")
                                        img_data = base64.b64decode(graphics[hist_key])
                                        st.image(img_data, use_column_width=True)
                                
                                if box_key in graphics:
                                    with col2:
                                        st.markdown("**Boxplot**")
                                        img_data = base64.b64decode(graphics[box_key])
                                        st.image(img_data, use_column_width=True)
                                
                                st.divider()
                    
                    # Log da execução R
                    if "r_output" in results and results["r_output"]:
                        with st.expander("🔍 Log da Execução R"):
                            st.code(results["r_output"])
                
                except Exception as e:
                    st.error(f"❌ Erro durante a análise: {str(e)}")
                    logger.error(f"Erro na análise R: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar dataset: {str(e)}")
        logger.error(f"Erro ao carregar dataset: {str(e)}")


def show_realtime_data_analysis():
    """Exibe análise dos dados coletados em tempo real."""
    st.subheader("⏰ Análise de Dados em Tempo Real")
    
    st.info("""
    **Dados dos Sensores IoT**
    
    Analisando dados coletados pelos sensores ESP32 em tempo real.
    """)
    
    # Verificar se R está disponível
    r_analyzer = RAnalyzer()
    r_available = r_analyzer.check_r_availability()
    
    # Adicionar informações de debug
    with st.expander("🔧 Debug - Informações do Sistema"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Ambiente Python:**")
            st.code(f"""
Virtual Env: {os.environ.get('VIRTUAL_ENV', 'Não detectada')}
Python: {sys.executable}
Working Dir: {os.getcwd()}
            """)
        
        with col2:
            st.markdown("**Detecção do R:**")
            if r_available:
                st.success(f"✅ R encontrado em: {r_analyzer.rscript_path}")
            else:
                st.error("❌ R não encontrado")
                
            if st.button("🔄 Forçar Nova Detecção do R"):
                # Criar nova instância para forçar nova detecção
                st.cache_data.clear()  # Limpar cache do Streamlit
                r_analyzer = RAnalyzer()  # Nova instância
                r_available = r_analyzer.check_r_availability(force_recheck=True)
                if r_available:
                    st.success(f"✅ R encontrado após nova detecção: {r_analyzer.rscript_path}")
                    st.rerun()
                else:
                    st.error("❌ R ainda não foi encontrado")
    
    if not r_available:
        return
    
    # Carregar dados recentes
    try:
        readings = get_recent_readings(1000)  # Últimas 1000 leituras
        
        if not readings:
            st.warning("⚠️ Nenhum dado encontrado. Verifique se o sistema de coleta está ativo.")
            st.markdown("""
            **Para coletar dados:**
            1. Execute o servidor: `python -m src.api.servidor`
            2. Configure o simulador ESP32 no Wokwi
            3. Pressione o botão na simulação para enviar dados
            """)
            return
        
        df = pd.DataFrame(readings)
        
        # Tratar timestamp se existir
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        # Métricas dos dados em tempo real
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Leituras", len(df))
        
        with col2:
            if 'timestamp' in df.columns:
                latest = df['timestamp'].max()
                oldest = df['timestamp'].min()
                period = latest - oldest
                st.metric("Período", f"{period.days} dias")
            else:
                st.metric("Período", "N/A")
        
        with col3:
            if 'potability' in df.columns:
                potable_count = df[df['potability'] == 1].shape[0]
                potable_pct = (potable_count / len(df)) * 100
                st.metric("% Potável", f"{potable_pct:.1f}%")
            else:
                st.metric("% Potável", "N/A")
        
        with col4:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            st.metric("Variáveis Numéricas", len(numeric_cols))
        
        # Prévia dos dados
        st.subheader("📋 Prévia dos Dados")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Configuração da análise
        st.subheader("🔬 Configuração da Análise")
        
        # Seleção de variáveis
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        if 'potability' in numeric_columns:
            numeric_columns.remove('potability')
        if 'id' in numeric_columns:
            numeric_columns.remove('id')
        
        if not numeric_columns:
            st.warning("⚠️ Nenhuma variável numérica encontrada nos dados.")
            return
        
        selected_vars = st.multiselect(
            "Selecione as variáveis para análise:",
            options=numeric_columns,
            default=numeric_columns,
            help="Escolha quais variáveis dos sensores analisar"
        )
        
        if not selected_vars:
            st.warning("⚠️ Selecione pelo menos uma variável para análise.")
            return
        
        # Tipos de análise
        analysis_types = st.multiselect(
            "Selecione os tipos de análise:",
            options=[
                "Medidas de Tendência Central",
                "Medidas de Dispersão", 
                "Medidas Separatrizes",
                "Gráficos (Histograma, Boxplot)",
                "Análise de Potabilidade",
                "Controle de Qualidade"
            ],
            default=["Medidas de Tendência Central", "Gráficos (Histograma, Boxplot)"]
        )
        
        # Configurações avançadas
        with st.expander("⚙️ Configurações Avançadas"):
            col1, col2 = st.columns(2)
            
            with col1:
                sample_size = st.number_input(
                    "Tamanho da Amostra", 
                    min_value=10, 
                    max_value=len(df), 
                    value=min(500, len(df)),
                    help="Número de registros mais recentes para análise"
                )
            
            with col2:
                remove_outliers = st.checkbox(
                    "Remover Outliers", 
                    value=False,
                    help="Remove valores extremos antes da análise"
                )
        
        if st.button("🚀 Executar Análises Estatísticas em R", type="primary"):
            
            # Preparar dados para análise
            analysis_df = df[selected_vars + (['potability'] if 'potability' in df.columns else [])].copy()
            
            # Usar apenas os registros mais recentes
            if len(analysis_df) > sample_size:
                analysis_df = analysis_df.tail(sample_size)
            
            # Remover outliers se solicitado
            if remove_outliers:
                Q1 = analysis_df[selected_vars].quantile(0.25)
                Q3 = analysis_df[selected_vars].quantile(0.75)
                IQR = Q3 - Q1
                mask = ~((analysis_df[selected_vars] < (Q1 - 1.5 * IQR)) | 
                        (analysis_df[selected_vars] > (Q3 + 1.5 * IQR))).any(axis=1)
                analysis_df = analysis_df[mask]
                st.info(f"📊 Dados após remoção de outliers: {len(analysis_df)} registros")
            
            with st.spinner("⏳ Executando análises estatísticas em R..."):
                
                try:
                    # Executar análise R
                    results = r_analyzer.analyze_data(analysis_df)
                    
                    if "error" in results:
                        st.error(f"❌ Erro na análise: {results['error']}")
                        return
                    
                    st.success("✅ Análises concluídas com sucesso!")
                    
                    # Sumário da análise
                    st.subheader("📋 Sumário da Análise")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Registros Analisados", len(analysis_df))
                    with col2:
                        st.metric("Variáveis", len(selected_vars))
                    with col3:
                        if 'timestamp' in df.columns:
                            latest_reading = df['timestamp'].max()
                            st.metric("Última Leitura", latest_reading.strftime("%d/%m/%Y %H:%M"))
                        else:
                            st.metric("Última Leitura", "N/A")
                    
                    # Exibir resultados estatísticos
                    if "statistics" in results and results["statistics"]:
                        st.subheader("📊 Resultados Estatísticos")
                        
                        for var, stats in results["statistics"].items():
                            st.markdown(f"### 📈 {var.title().replace('_', ' ')}")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            # Tendência central
                            if "tendencia_central" in stats:
                                with col1:
                                    st.markdown("**Tendência Central**")
                                    tc = stats["tendencia_central"]
                                    st.metric("Média", f"{tc.get('media', 0):.4f}")
                                    st.metric("Mediana", f"{tc.get('mediana', 0):.4f}")
                                    if not pd.isna(tc.get('moda', 0)):
                                        st.metric("Moda", f"{tc.get('moda', 0):.4f}")
                            
                            # Dispersão
                            if "dispersao" in stats:
                                with col2:
                                    st.markdown("**Dispersão**")
                                    disp = stats["dispersao"]
                                    st.metric("Variância", f"{disp.get('variancia', 0):.4f}")
                                    st.metric("Desvio Padrão", f"{disp.get('desvio_padrao', 0):.4f}")
                                    st.metric("Amplitude", f"{disp.get('amplitude', 0):.4f}")
                                    st.metric("IQR", f"{disp.get('iqr', 0):.4f}")
                            
                            # Separatrizes
                            if "separatrizes" in stats:
                                with col3:
                                    st.markdown("**Separatrizes**")
                                    sep = stats["separatrizes"]
                                    
                                    if "quartis" in sep:
                                        quartis = sep["quartis"]
                                        # quartis vem como lista [Q1, Q2, Q3] do R
                                        if isinstance(quartis, list) and len(quartis) >= 3:
                                            st.metric("Q1", f"{quartis[0]:.4f}")
                                            st.metric("Q2 (Mediana)", f"{quartis[1]:.4f}")
                                            st.metric("Q3", f"{quartis[2]:.4f}")
                                        elif isinstance(quartis, dict):
                                            # Fallback para formato de dicionário
                                            st.metric("Q1", f"{quartis.get('25%', 0):.4f}")
                                            st.metric("Q2 (Mediana)", f"{quartis.get('50%', 0):.4f}")
                                            st.metric("Q3", f"{quartis.get('75%', 0):.4f}")
                            
                            st.divider()
                    
                    # Exibir gráficos
                    if "graphics" in results and results["graphics"]:
                        st.subheader("📊 Visualizações")
                        
                        graphics = results["graphics"]
                        
                        # Gráfico de potabilidade (se disponível)
                        if "barplot_potability" in graphics:
                            st.markdown("### 📊 Distribuição de Potabilidade")
                            img_data = base64.b64decode(graphics["barplot_potability"])
                            st.image(img_data, use_column_width=True)
                            st.divider()
                        
                        # Histogramas e boxplots para cada variável
                        for var in selected_vars:
                            hist_key = f"histogram_{var}"
                            box_key = f"boxplot_{var}"
                            
                            if hist_key in graphics or box_key in graphics:
                                st.markdown(f"### 📈 {var.title().replace('_', ' ')}")
                                
                                col1, col2 = st.columns(2)
                                
                                if hist_key in graphics:
                                    with col1:
                                        st.markdown("**Histograma**")
                                        img_data = base64.b64decode(graphics[hist_key])
                                        st.image(img_data, use_column_width=True)
                                
                                if box_key in graphics:
                                    with col2:
                                        st.markdown("**Boxplot**")
                                        img_data = base64.b64decode(graphics[box_key])
                                        st.image(img_data, use_column_width=True)
                                
                                st.divider()
                    
                    # Insights e recomendações
                    st.subheader("💡 Insights e Recomendações")
                    
                    insights = []
                    
                    if "statistics" in results:
                        for var, stats in results["statistics"].items():
                            if "dispersao" in stats:
                                cv = stats["dispersao"]["desvio_padrao"] / abs(stats["tendencia_central"]["media"]) * 100
                                if cv > 30:
                                    insights.append(f"🔍 **{var}**: Alta variabilidade detectada (CV={cv:.1f}%) - verificar calibração do sensor")
                                elif cv < 5:
                                    insights.append(f"✅ **{var}**: Baixa variabilidade (CV={cv:.1f}%) - sensor estável")
                    
                    if insights:
                        for insight in insights:
                            st.markdown(insight)
                    else:
                        st.info("📊 Dados dentro dos padrões esperados.")
                    
                    # Log da execução R
                    if "r_output" in results and results["r_output"]:
                        with st.expander("🔍 Log da Execução R"):
                            st.code(results["r_output"])
                
                except Exception as e:
                    st.error(f"❌ Erro durante a análise: {str(e)}")
                    logger.error(f"Erro na análise R: {str(e)}")
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        logger.error(f"Erro ao carregar dados em tempo real: {str(e)}")


if __name__ == "__main__":
    main() 
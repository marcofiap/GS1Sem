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

# Adicionar o diretório src ao path para importações
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.api.controller import get_controller
from src.utils.logging import setup_logging, get_logger

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
        ["Dashboard", "Análise Detalhada", "Dataset", "Histórico", "Alertas", "Configurações"]
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


if __name__ == "__main__":
    main() 
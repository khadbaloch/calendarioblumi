import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

# ===== CONFIGURAÇÃO DA PÁGINA =====
st.set_page_config(
    page_title="Blūmi Talents - Agenda de Eventos",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== ESTILO CSS PERSONALIZADO =====
st.markdown("""
<style>
    /* Importar fonte Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Reset e fonte global */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Fundo da página */
    .main {
        background-color: #FAFBFC;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
    }
    
    /* Títulos simples */
    h1 {
        color: #1A1A1A;
        font-weight: 600;
        font-size: 2rem;
    }
    
    h2 {
        color: #1A1A1A;
        font-weight: 600;
        font-size: 1.5rem;
    }
    
    h3 {
        color: #1A1A1A;
        font-weight: 600;
        font-size: 1.2rem;
    }
    
    /* Remover padding excessivo */
    .block-container {
        padding: 2rem 1rem;
    }
    
    /* Métricas */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1A1A1A;
    }
</style>
""", unsafe_allow_html=True)

# ===== FUNÇÃO DE CARREGAMENTO DE DADOS =====
@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_events_from_csv():
    """Carrega os eventos do CSV público do Google Sheets"""
    try:
        # URL do CSV público - ABA: Registro_eventos
        # IMPORTANTE: Certifique-se de que a aba "Registro_eventos" está publicada
        CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaDzfwhQrA8vGBdTYMQxMtWE-ABiSDqBpxxfVQMrJcvNC0sSqOEH6wj7Gvk3oTQhDzMJmWFEw3yQyL/pub?output=csv"
        
        # Carregar dados com timeout
        df = pd.read_csv(CSV_URL, encoding='utf-8')
        
        # Verificar se tem as colunas esperadas
        expected_cols = ['Nome', 'Data início', 'Data Final', 'Tipo de evento', 'Universidade']
        missing_cols = [col for col in expected_cols if col not in df.columns]
        
        if missing_cols:
            st.error(f"⚠️ Colunas faltando na planilha: {missing_cols}")
            st.info("📌 Verifique se a aba 'Registro_eventos' está sendo publicada como CSV")
            return None
        
        # Processar datas
        df['Data início'] = pd.to_datetime(df['Data início'], errors='coerce', dayfirst=True)
        df['Data Final'] = pd.to_datetime(df['Data Final'], errors='coerce', dayfirst=True)
        
        # Remover linhas completamente vazias
        df = df.dropna(how='all')
        
        return df
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        st.info("""
        **Possíveis causas:**
        1. A aba 'Registro_eventos' não está publicada como CSV
        2. URL do CSV incorreta
        3. Problema de conexão com o Google Sheets
        
        **Como resolver:**
        - Vá em Arquivo → Compartilhar → Publicar na Web
        - Selecione a aba 'Registro_eventos'
        - Formato: CSV
        - Publique e use o novo link
        """)
        return None

def get_event_color(tipo_evento):
    """Retorna a cor correspondente ao tipo de evento"""
    if pd.isna(tipo_evento):
        return '#9E9E9E', 'outros'
    
    tipo_lower = str(tipo_evento).lower()
    
    if 'feira' in tipo_lower:
        return '#FF6B8A', 'feira'
    elif 'live' in tipo_lower:
        return '#00D9FF', 'live'
    elif 'circle' in tipo_lower or 'círculo' in tipo_lower:
        return '#D4FF33', 'circle'
    else:
        return '#9E9E9E', 'outros'

def get_event_tag_class(tipo_evento):
    """Retorna a classe CSS para a tag do tipo de evento"""
    if pd.isna(tipo_evento):
        return 'tag-outros'
    
    tipo_lower = str(tipo_evento).lower()
    
    if 'feira' in tipo_lower:
        return 'tag-feira'
    elif 'live' in tipo_lower:
        return 'tag-live'
    elif 'circle' in tipo_lower or 'círculo' in tipo_lower:
        return 'tag-circle'
    else:
        return 'tag-outros'

# ===== INTERFACE PRINCIPAL =====
def main():
    # Cabeçalho
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.title("📅 Agenda de Eventos")
        st.caption("Blūmi Talents - Acompanhe todos os eventos e feiras")
    
    with col2:
        st.link_button(
            "📊 Ver Planilha",
            "https://docs.google.com/spreadsheets/d/1J7baToo2UjdEJp8jtWc_7tYdQN_kJPmErKIR_9ByvL4/edit",
            use_container_width=True
        )
    
    st.divider()
    
    # Carregar dados
    with st.spinner("⏳ Carregando eventos da planilha..."):
        df = load_events_from_csv()
    
    if df is None:
        st.stop()
    
    if df.empty:
        st.warning("⚠️ Nenhum evento encontrado na planilha.")
        st.info("Verifique se a aba 'Registro_eventos' tem dados e está publicada corretamente.")
        st.stop()
    
    # ===== SIDEBAR - FILTROS =====
    with st.sidebar:
        st.header("🎯 Filtros")
        
        # Filtro por tipo de evento
        tipos_evento = ['Todos'] + sorted(df['Tipo de evento'].dropna().unique().tolist())
        tipo_selecionado = st.selectbox(
            "Tipo de Evento",
            tipos_evento,
            index=0
        )
        
        # Filtro por mês
        meses = {
            'Todos': None,
            'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4,
            'Maio': 5, 'Junho': 6, 'Julho': 7, 'Agosto': 8,
            'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
        }
        mes_selecionado = st.selectbox(
            "Mês",
            list(meses.keys()),
            index=0
        )
        
        # Filtro por universidade
        universidades = ['Todas'] + sorted(df['Universidade'].dropna().unique().tolist())
        universidade_selecionada = st.selectbox(
            "Universidade",
            universidades,
            index=0
        )
        
        st.divider()
        
        st.caption("📍 Dados em tempo real")
        st.caption("🔄 Atualização a cada 5min")
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if tipo_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Tipo de evento'] == tipo_selecionado]
    
    if mes_selecionado != 'Todos':
        mes_num = meses[mes_selecionado]
        df_filtrado = df_filtrado[df_filtrado['Data início'].dt.month == mes_num]
    
    if universidade_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Universidade'] == universidade_selecionada]
    
    # ===== MÉTRICAS =====
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📅 Total de Eventos", len(df_filtrado))
    
    with col2:
        eventos_mes = len(df_filtrado[df_filtrado['Data início'].dt.month == datetime.now().month])
        st.metric("📆 Eventos este Mês", eventos_mes)
    
    with col3:
        eventos_futuros = len(df_filtrado[df_filtrado['Data início'] >= datetime.now()])
        st.metric("🔜 Próximos Eventos", eventos_futuros)
    
    with col4:
        universidades_unicas = df_filtrado['Universidade'].nunique()
        st.metric("🎓 Universidades", universidades_unicas)
    
    st.divider()
    
    # ===== VISUALIZAÇÃO =====
    tab1, tab2 = st.tabs(["📋 Lista de Eventos", "📅 Visão Calendário"])
    
    with tab1:
        # Lista de eventos
        st.subheader("📋 Próximos Eventos")
        
        if len(df_filtrado) == 0:
            st.info("Nenhum evento encontrado com os filtros selecionados.")
        else:
            # Ordenar por data
            df_ordenado = df_filtrado.sort_values('Data início')
            
            for idx, row in df_ordenado.iterrows():
                color, tipo_class = get_event_color(row['Tipo de evento'])
                
                data_inicio = row['Data início']
                data_fim = row['Data Final']
                
                # Formatar datas
                if pd.notna(data_inicio):
                    data_inicio_str = data_inicio.strftime('%d/%m/%Y')
                else:
                    data_inicio_str = 'Data não definida'
                
                if pd.notna(data_fim):
                    data_fim_str = data_fim.strftime('%d/%m/%Y')
                else:
                    data_fim_str = data_inicio_str
                
                tipo_evento_display = row['Tipo de evento'] if pd.notna(row['Tipo de evento']) else 'Não definido'
                universidade_display = row['Universidade'] if pd.notna(row['Universidade']) else 'Não definida'
                
                # Container simples para cada evento
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{row['Nome']}**")
                        st.caption(f"📅 {data_inicio_str} - {data_fim_str} | 🎓 {universidade_display}")
                    
                    with col2:
                        # Badge de tipo
                        st.markdown(
                            f'<span style="background-color: {color}; color: white; padding: 4px 12px; '
                            f'border-radius: 12px; font-size: 0.75rem; font-weight: 600;">'
                            f'{tipo_evento_display}</span>',
                            unsafe_allow_html=True
                        )
                    
                    st.divider()
    
    with tab2:
        # Visão de calendário
        st.subheader("📅 Calendário de Eventos")
        
        # Controles
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            ano_cal = st.selectbox("Ano", range(2024, 2027), index=1, key="ano_cal")
        
        with col2:
            meses_pt = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                       'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            mes_cal = st.selectbox("Mês", range(1, 13), 
                                   format_func=lambda x: meses_pt[x-1],
                                   index=datetime.now().month - 1,
                                   key="mes_cal")
        
        with col3:
            if st.button("Hoje", use_container_width=True, key="btn_hoje"):
                st.rerun()
        
        st.write("")  # Espaço
        
        # Criar DataFrame para o calendário
        cal = calendar.monthcalendar(ano_cal, mes_cal)
        
        # Mostrar eventos do mês em lista simples
        eventos_mes = df_filtrado[
            (df_filtrado['Data início'].dt.month == mes_cal) &
            (df_filtrado['Data início'].dt.year == ano_cal)
        ].sort_values('Data início')
        
        if len(eventos_mes) > 0:
            st.write(f"**{len(eventos_mes)} eventos em {meses_pt[mes_cal-1]}**")
            st.write("")
            
            for _, evento in eventos_mes.iterrows():
                color, _ = get_event_color(evento['Tipo de evento'])
                
                data_inicio = evento['Data início']
                if pd.notna(data_inicio):
                    dia = data_inicio.day
                    data_str = data_inicio.strftime('%d/%m')
                else:
                    dia = "?"
                    data_str = "?"
                
                tipo = evento['Tipo de evento'] if pd.notna(evento['Tipo de evento']) else 'Evento'
                
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    st.markdown(
                        f'<div style="background: {color}; color: white; padding: 8px; '
                        f'border-radius: 8px; text-align: center; font-weight: 600;">'
                        f'{dia}</div>',
                        unsafe_allow_html=True
                    )
                
                with col2:
                    st.markdown(f"**{evento['Nome']}**")
                    st.caption(f"{tipo} | {data_str}")
                
                st.write("")
        else:
            st.info(f"Nenhum evento em {meses_pt[mes_cal-1]} {ano_cal}")
        
        # Legenda simples
        st.divider()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('🟥 **Feiras**')
        with col2:
            st.markdown('🟦 **Lives**')
        with col3:
            st.markdown('🟩 **Circles**')
        with col4:
            st.markdown('⬜ **Outros**')
    
    # Footer
    st.divider()
    st.caption("**blūmi talents** | Transformando a contratação de jovens talentos | @blumi_talents")

if __name__ == "__main__":
    main()

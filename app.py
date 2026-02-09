import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

# ===== CONFIGURAÇÃO DA PÁGINA =====
st.set_page_config(
    page_title="Blūmi Talents - Agenda de Eventos",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===== ESTILO CSS MINIMALISTA =====
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Fundo branco */
    .main {
        background-color: #FFFFFF;
        padding: 32px;
    }
    
    /* Sidebar com fundo claro e fonte escura */
    [data-testid="stSidebar"] {
        background-color: #F8F9FA !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #1A1A1A !important;
    }
    
    /* Header limpo */
    h1 {
        color: #1A1A1A;
        font-weight: 600;
        font-size: 1.8rem;
        margin-bottom: 8px;
    }
    
    h2 {
        color: #1A1A1A;
        font-weight: 600;
        font-size: 1.4rem;
    }
    
    h3 {
        color: #1A1A1A;
        font-weight: 600;
        font-size: 1.2rem;
    }
    
    /* Remover espaçamento excessivo */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Métricas visíveis - fonte clara */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1A1A1A !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #5F6368 !important;
    }
    
    /* Botões navegação alinhados */
    .stButton > button {
        background-color: #FFFFFF;
        border: 1px solid #DADCE0;
        border-radius: 4px;
        color: #1A1A1A;
        font-weight: 500;
        padding: 8px 16px;
        height: 40px;
    }
    
    .stButton > button:hover {
        background-color: #F8F9FA;
        border-color: #DADCE0;
    }
    
    /* Selectbox escuro */
    .stSelectbox label {
        color: #1A1A1A !important;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ===== CARREGAR DADOS =====
@st.cache_data(ttl=300)
def load_events_from_csv():
    """Carrega eventos do CSV público"""
    try:
        CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaDzfwhQrA8vGBdTYMQxMtWE-ABiSDqBpxxfVQMrJcvNC0sSqOEH6wj7Gvk3oTQhDzMJmWFEw3yQyL/pub?output=csv"
        df = pd.read_csv(CSV_URL, encoding='utf-8')
        
        # Processar datas
        df['Data início'] = pd.to_datetime(df['Data início'], errors='coerce', dayfirst=True)
        df['Data Final'] = pd.to_datetime(df['Data Final'], errors='coerce', dayfirst=True)
        
        # Remover linhas vazias
        df = df.dropna(how='all')
        
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        return None

def get_event_color(tipo_evento):
    """Retorna cor do tipo de evento"""
    if pd.isna(tipo_evento):
        return '#9E9E9E'
    
    tipo_lower = str(tipo_evento).lower()
    
    if 'feira' in tipo_lower:
        return '#FF6B8A'  # Rosa
    elif 'live' in tipo_lower:
        return '#00D9FF'  # Azul
    elif 'circle' in tipo_lower or 'círculo' in tipo_lower:
        return '#D4FF33'  # Verde limão
    else:
        return '#9E9E9E'  # Cinza

# ===== MAIN =====
def main():
    # Carregar dados
    df = load_events_from_csv()
    
    if df is None or df.empty:
        st.error("Não foi possível carregar os eventos.")
        st.stop()
    
    # ===== HEADER =====
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.title("📅 Agenda de Eventos Blūmi")
        st.caption("Acompanhe todos os eventos e feiras")
    
    with col2:
        st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
        st.link_button(
            "📊 Ver Planilha",
            "https://docs.google.com/spreadsheets/d/1J7baToo2UjdEJp8jtWc_7tYdQN_kJPmErKIR_9ByvL4/edit",
            use_container_width=True
        )
    
    st.divider()
    
    # ===== CONTROLES DE NAVEGAÇÃO =====
    # Inicializar estado
    if 'current_month' not in st.session_state:
        st.session_state.current_month = datetime.now().month
    if 'current_year' not in st.session_state:
        st.session_state.current_year = datetime.now().year
    
    col1, col2, col3, col4, col5 = st.columns([1, 1, 3, 1, 1])
    
    with col1:
        if st.button("◀ Anterior", key="prev_month", use_container_width=True):
            if st.session_state.current_month == 1:
                st.session_state.current_month = 12
                st.session_state.current_year -= 1
            else:
                st.session_state.current_month -= 1
            st.rerun()
    
    with col2:
        if st.button("📅 Hoje", key="today", use_container_width=True):
            st.session_state.current_month = datetime.now().month
            st.session_state.current_year = datetime.now().year
            st.rerun()
    
    with col3:
        # Título do mês centralizado
        meses_pt = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        mes_atual = st.session_state.current_month
        ano_atual = st.session_state.current_year
        
        st.markdown(f"""
        <div style='text-align: center; padding: 8px 0;'>
            <span style='font-size: 1.5rem; font-weight: 600; color: #1A1A1A;'>
                {meses_pt[mes_atual - 1]} {ano_atual}
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Espaço vazio para simetria
        st.write("")
    
    with col5:
        if st.button("Próximo ▶", key="next_month", use_container_width=True):
            if st.session_state.current_month == 12:
                st.session_state.current_month = 1
                st.session_state.current_year += 1
            else:
                st.session_state.current_month += 1
            st.rerun()
    
    st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)
    
    # ===== CALENDÁRIO =====
    mes = st.session_state.current_month
    ano = st.session_state.current_year
    
    # Configurar calendário para começar no domingo (padrão brasileiro)
    calendar.setfirstweekday(calendar.SUNDAY)
    
    # Gerar calendário
    cal = calendar.monthcalendar(ano, mes)
    hoje = datetime.now().date()
    
    # Header dos dias da semana (DOM - SÁB)
    dias_semana = ['DOM', 'SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SÁB']
    
    # Criar header
    cols_header = st.columns(7)
    for idx, dia in enumerate(dias_semana):
        with cols_header[idx]:
            st.markdown(f"""
            <div style='text-align: center; padding: 12px; background: #F8F9FA; 
                        font-weight: 600; font-size: 0.75rem; color: #5F6368; 
                        border-radius: 4px;'>
                {dia}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 4px 0;'></div>", unsafe_allow_html=True)
    
    # Grid do calendário - uma semana por vez
    for semana in cal:
        cols = st.columns(7)
        
        for idx, dia in enumerate(semana):
            with cols[idx]:
                if dia == 0:
                    # Dia vazio
                    st.markdown("""
                    <div style='background: #FAFAFA; min-height: 100px; border: 1px solid #E0E0E0; 
                                border-radius: 4px; padding: 8px;'>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    data_dia = datetime(ano, mes, dia).date()
                    
                    # Buscar eventos deste dia
                    eventos_dia = df[
                        (df['Data início'].dt.date <= data_dia) &
                        (df['Data Final'].dt.date >= data_dia)
                    ]
                    
                    # Estilo do dia
                    is_today = data_dia == hoje
                    
                    if is_today:
                        bg_color = "#E8F4FD"
                        dia_color = "#1967D2"
                        dia_weight = "700"
                        border_color = "#1967D2"
                    else:
                        bg_color = "#FFFFFF"
                        dia_color = "#1A1A1A"
                        dia_weight = "500"
                        border_color = "#E0E0E0"
                    
                    # Montar HTML do dia
                    dia_html = f"""
                    <div style='background: {bg_color}; min-height: 100px; border: 1px solid {border_color}; 
                                border-radius: 4px; padding: 8px;'>
                        <div style='font-size: 0.875rem; color: {dia_color}; font-weight: {dia_weight}; 
                                    margin-bottom: 4px;'>
                            {dia}
                        </div>
                    """
                    
                    # Adicionar eventos (máximo 3)
                    for _, evento in eventos_dia.head(3).iterrows():
                        color = get_event_color(evento['Tipo de evento'])
                        nome = str(evento['Nome'])
                        
                        # Truncar nome
                        if len(nome) > 15:
                            nome = nome[:12] + "..."
                        
                        dia_html += f"""
                        <div style='background: {color}; color: white; padding: 2px 4px; 
                                    margin-bottom: 2px; border-radius: 3px; font-size: 0.65rem; 
                                    font-weight: 500; white-space: nowrap; overflow: hidden; 
                                    text-overflow: ellipsis;'>
                            {nome}
                        </div>
                        """
                    
                    # Indicador de mais eventos
                    if len(eventos_dia) > 3:
                        dia_html += f"""
                        <div style='font-size: 0.6rem; color: #5F6368; margin-top: 2px;'>
                            +{len(eventos_dia) - 3} mais
                        </div>
                        """
                    
                    dia_html += "</div>"
                    
                    st.markdown(dia_html, unsafe_allow_html=True)
        
        st.markdown("<div style='margin: 4px 0;'></div>", unsafe_allow_html=True)
    
    # ===== LEGENDA =====
    st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style='display: flex; align-items: center; gap: 8px;'>
            <div style='width: 16px; height: 16px; background: #FF6B8A; border-radius: 3px;'></div>
            <span style='font-size: 0.875rem; color: #5F6368;'>Feiras</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='display: flex; align-items: center; gap: 8px;'>
            <div style='width: 16px; height: 16px; background: #00D9FF; border-radius: 3px;'></div>
            <span style='font-size: 0.875rem; color: #5F6368;'>Lives</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='display: flex; align-items: center; gap: 8px;'>
            <div style='width: 16px; height: 16px; background: #D4FF33; border-radius: 3px;'></div>
            <span style='font-size: 0.875rem; color: #5F6368;'>Circles</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style='display: flex; align-items: center; gap: 8px;'>
            <div style='width: 16px; height: 16px; background: #9E9E9E; border-radius: 3px;'></div>
            <span style='font-size: 0.875rem; color: #5F6368;'>Outros</span>
        </div>
        """, unsafe_allow_html=True)
    
    # ===== LISTA DE EVENTOS DO MÊS =====
    st.markdown("<div style='margin-top: 48px;'></div>", unsafe_allow_html=True)
    
    eventos_mes = df[
        (df['Data início'].dt.month == mes) &
        (df['Data início'].dt.year == ano)
    ].sort_values('Data início')
    
    if len(eventos_mes) > 0:
        st.markdown(f"### Eventos de {meses_pt[mes-1]} ({len(eventos_mes)})")
        st.markdown("<div style='margin: 16px 0;'></div>", unsafe_allow_html=True)
        
        for _, evento in eventos_mes.iterrows():
            color = get_event_color(evento['Tipo de evento'])
            
            data_inicio = evento['Data início']
            data_fim = evento['Data Final']
            
            if pd.notna(data_inicio):
                data_str = data_inicio.strftime('%d/%m/%Y')
                if pd.notna(data_fim) and data_fim != data_inicio:
                    data_str += " - " + data_fim.strftime('%d/%m/%Y')
            else:
                data_str = "Data não definida"
            
            tipo = evento['Tipo de evento'] if pd.notna(evento['Tipo de evento']) else 'Evento'
            univ = evento['Universidade'] if pd.notna(evento['Universidade']) else ''
            
            st.markdown(f"""
            <div style='border-left: 4px solid {color}; padding: 12px 16px; margin-bottom: 8px; 
                        background: #F8F9FA; border-radius: 0 4px 4px 0;'>
                <div style='font-weight: 600; color: #1A1A1A; margin-bottom: 4px;'>
                    {evento['Nome']}
                </div>
                <div style='font-size: 0.875rem; color: #5F6368;'>
                    {tipo} • {data_str} {f"• {univ}" if univ else ""}
                </div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

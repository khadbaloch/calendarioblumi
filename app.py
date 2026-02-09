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
    
    /* Headers */
    h1 {
        font-weight: 600;
        font-size: 1.8rem;
    }
    
    /* Botões */
    .stButton > button {
        border-radius: 4px;
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
        
        st.markdown(f"### {meses_pt[mes_atual - 1]} {ano_atual}", 
                   unsafe_allow_html=False)
    
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
    
    
    # Grid do calendário - uma semana por vez
    for semana in cal:
        cols = st.columns(7)
        
        for idx, dia in enumerate(semana):
            with cols[idx]:
                if dia == 0:
                    # Dia vazio - container vazio
                    st.container(height=120, border=True)
                else:
                    data_dia = datetime(ano, mes, dia).date()
                    
                    # Buscar eventos deste dia
                    # Se Data Final é nula, considera apenas Data início
                    eventos_range = df[
                        (df['Data início'].dt.date <= data_dia) &
                        (df['Data Final'].dt.date >= data_dia) &
                        (df['Data Final'].notna())
                    ]
                    
                    eventos_sem_fim = df[
                        (df['Data início'].dt.date == data_dia) &
                        (df['Data Final'].isna())
                    ]
    
    st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)
    
    # =====ABAS =====
    tab1, tab2 = st.tabs(["📅 Calendário", "📋 Todos os Eventos"])
    
    with tab1:
        # Variáveis do mês atual
        mes = st.session_state.current_month
        ano = st.session_state.current_year
        meses_pt = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        
        # ===== CALENDÁRIO =====
        # Configurar calendário para começar no domingo
        calendar.setfirstweekday(calendar.SUNDAY)
        
        # Gerar calendário
        cal = calendar.monthcalendar(ano, mes)
        hoje = datetime.now().date()
        
        # Header dos dias da semana
        dias_semana = ['DOM', 'SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SÁB']
        
        cols_header = st.columns(7)
        for idx, dia in enumerate(dias_semana):
            with cols_header[idx]:
                st.markdown(f"**{dia}**")
        
        st.markdown("<div style='margin: 4px 0;'></div>", unsafe_allow_html=True)
        
        # Grid do calendário
        for semana in cal:
            cols = st.columns(7)
            
            for idx, dia in enumerate(semana):
                with cols[idx]:
                    if dia == 0:
                        st.container(height=120, border=True)
                    else:
                        data_dia = datetime(ano, mes, dia).date()
                        
                        # Buscar eventos deste dia
                        eventos_range = df[
                            (df['Data início'].dt.date <= data_dia) &
                            (df['Data Final'].dt.date >= data_dia) &
                            (df['Data Final'].notna())
                        ]
                        
                        eventos_sem_fim = df[
                            (df['Data início'].dt.date == data_dia) &
                            (df['Data Final'].isna())
                        ]
                        
                        eventos_dia = pd.concat([eventos_range, eventos_sem_fim]).drop_duplicates()
                        eventos_dia = eventos_dia.sort_values('Data início')
                        
                        is_today = data_dia == hoje
                        
                        with st.container(height=120, border=True):
                            # Número do dia
                            if is_today:
                                st.markdown(f"**:blue[{dia}]**")
                            else:
                                st.markdown(f"**{dia}**")
                            
                            # Mostrar eventos como badges coloridas (máximo 3)
                            num_eventos = len(eventos_dia)
                            
                            for _, evento in eventos_dia.head(3).iterrows():
                                color = get_event_color(evento['Tipo de evento'])
                                nome = str(evento['Nome'])
                                
                                # Truncar nome
                                if len(nome) > 15:
                                    nome_display = nome[:13] + ".."
                                else:
                                    nome_display = nome
                                
                                # Badge colorida estilo Google Calendar
                                st.markdown(
                                    f'<div style="background:{color}; color:white; '
                                    f'padding:2px 6px; margin:2px 0; border-radius:3px; '
                                    f'font-size:0.7rem; font-weight:500; '
                                    f'white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" '
                                    f'title="{nome}">'
                                    f'{nome_display}</div>',
                                    unsafe_allow_html=True
                                )
                            
                            # Indicador de mais eventos
                            if num_eventos > 3:
                                st.caption(f"+{num_eventos - 3} mais")
            
            st.write("")
        
        # Legenda
        st.write("")
        st.write("")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("🟥 **Feiras**")
        
        with col2:
            st.markdown("🟦 **Lives**")
        
        with col3:
            st.markdown("🟩 **Circles**")
        
        with col4:
            st.markdown("⬜ **Outros**")
        
        # ===== LISTA DE EVENTOS DO MÊS =====
        st.divider()
        st.subheader(f"Eventos de {meses_pt[mes-1]} {ano}")
        
        eventos_mes = df[
            (df['Data início'].dt.month == mes) &
            (df['Data início'].dt.year == ano)
        ].sort_values('Data início')
        
        if len(eventos_mes) > 0:
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
                
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"**{evento['Nome']}**")
                    st.caption(f"📅 {data_str} • {tipo} {f'• 🎓 {univ}' if univ else ''}")
                
                with col2:
                    # Emoji indicador
                    if 'feira' in str(tipo).lower():
                        st.markdown("### 🟥")
                    elif 'live' in str(tipo).lower():
                        st.markdown("### 🟦")
                    elif 'circle' in str(tipo).lower():
                        st.markdown("### 🟩")
                    else:
                        st.markdown("### ⬜")
                
                st.divider()
        else:
            st.info(f"Nenhum evento em {meses_pt[mes-1]} {ano}")
    
    with tab2:
        # ===== LISTA COMPLETA DE EVENTOS =====
        st.subheader("📋 Todos os Eventos")
        st.caption("Lista completa de eventos da Blūmi Talents")
        st.write("")
        
        # Todos os eventos ordenados por data
        df_todos = df.sort_values('Data início')
        
        for _, evento in df_todos.iterrows():
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
            
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"**{evento['Nome']}**")
                st.caption(f"📅 {data_str} • 🏷️ {tipo} {f'• 🎓 {univ}' if univ else ''}")
            
            with col2:
                # Badge colorida com o nome do tipo
                st.markdown(
                    f'<div style="background:{color}; color:white; padding:8px 12px; '
                    f'border-radius:6px; text-align:center; font-size:0.75rem; font-weight:600;">'
                    f'{tipo}</div>',
                    unsafe_allow_html=True
                )
            
            st.divider()

if __name__ == "__main__":
    main()

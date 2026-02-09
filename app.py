import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    /* Aplicar fonte globalmente */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Fundo geral */
    .main {
        background-color: #F2F4F6;
        padding: 48px 24px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        padding: 32px 16px;
    }
    
    /* Títulos */
    h1 {
        color: #3B4B5E;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 8px;
    }
    
    h2 {
        color: #3B4B5E;
        font-weight: 600;
        font-size: 1.8rem;
        margin-top: 32px;
        margin-bottom: 24px;
    }
    
    h3 {
        color: #3B4B5E;
        font-weight: 600;
        font-size: 1.3rem;
        margin-bottom: 16px;
    }
    
    /* Cards de seção */
    .section-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 32px;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    
    /* Cards de eventos */
    .event-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        border-left: 4px solid;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
    }
    
    .event-card:hover {
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    /* Cores das tags de tipo de evento */
    .event-card.feira { border-left-color: #FF6B8A; }
    .event-card.live { border-left-color: #00D9FF; }
    .event-card.circle { border-left-color: #D4FF33; }
    .event-card.outros { border-left-color: #9E9E9E; }
    
    /* Tags de tipo */
    .event-tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 8px;
    }
    
    .tag-feira { background-color: #FFE5EC; color: #C91952; }
    .tag-live { background-color: #E0F9FF; color: #007A8C; }
    .tag-circle { background-color: #F5FFD6; color: #5A6B00; }
    .tag-outros { background-color: #F5F5F5; color: #424242; }
    
    /* Botão secundário customizado */
    .stButton > button {
        background-color: #FFFFFF;
        color: #3B4B5E;
        border: 1px solid #D8DEE6;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #F2F4F6;
        border-color: #3B4B5E;
    }
    
    /* Calendário */
    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 8px;
        margin-top: 16px;
    }
    
    .calendar-day {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 12px 8px;
        text-align: center;
        min-height: 100px;
        position: relative;
        border: 1px solid #E8EBF0;
    }
    
    .calendar-day-header {
        font-weight: 600;
        color: #3B4B5E;
        font-size: 0.85rem;
        margin-bottom: 8px;
    }
    
    .calendar-day-number {
        font-size: 1.1rem;
        color: #3B4B5E;
        font-weight: 600;
        margin-bottom: 4px;
    }
    
    .calendar-day.has-event {
        background-color: #F0FFF4;
        border-color: #D4FF33;
    }
    
    .calendar-day.today {
        background-color: #E0F9FF;
        border-color: #00D9FF;
        border-width: 2px;
    }
    
    .event-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
        margin: 2px;
    }
    
    /* Remover padding padrão */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Métricas */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #3B4B5E;
    }
    
    /* Filtros na sidebar */
    .sidebar-filter-section {
        margin-bottom: 24px;
    }
</style>
""", unsafe_allow_html=True)

# ===== FUNÇÕES DE CONEXÃO COM GOOGLE SHEETS =====
@st.cache_resource
def get_google_sheets_service():
    """Conecta ao Google Sheets usando credenciais do Streamlit Secrets"""
    try:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except Exception as e:
        st.error(f"Erro ao conectar com Google Sheets: {e}")
        return None

@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_events_from_sheets():
    """Carrega os eventos da planilha do Google Sheets"""
    try:
        service = get_google_sheets_service()
        if service is None:
            return None
        
        # ID da planilha (extraído da URL)
        SPREADSHEET_ID = '1J7baToo2UjdEJp8jtWc_7tYdQN_kJPmErKIR_9ByvL4'
        RANGE_NAME = 'Página1!A:E'  # Ajuste conforme o nome da aba
        
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            st.warning('Nenhum dado encontrado na planilha.')
            return None
        
        # Criar DataFrame
        df = pd.DataFrame(values[1:], columns=values[0])
        
        # Processar datas
        df['Data início'] = pd.to_datetime(df['Data início'], errors='coerce')
        df['Data Final'] = pd.to_datetime(df['Data Final'], errors='coerce')
        
        return df
    
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

def get_event_color(tipo_evento):
    """Retorna a cor correspondente ao tipo de evento"""
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
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        <div style='margin-bottom: 32px;'>
            <h1>📅 Agenda de Eventos Blūmi</h1>
            <p style='color: #6B7A8F; font-size: 1.1rem;'>
                Acompanhe todos os eventos, feiras e ações da Blūmi Talents
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("📊 Abrir Planilha Original", use_container_width=True):
            st.markdown(
                """<script>window.open('https://docs.google.com/spreadsheets/d/1J7baToo2UjdEJp8jtWc_7tYdQN_kJPmErKIR_9ByvL4/edit', '_blank')</script>""",
                unsafe_allow_html=True
            )
    
    # Carregar dados
    df = load_events_from_sheets()
    
    if df is None or df.empty:
        st.error("Não foi possível carregar os eventos. Verifique a conexão com o Google Sheets.")
        st.info("""
        **Instruções de configuração:**
        1. Configure as credenciais do Google Cloud no arquivo `.streamlit/secrets.toml`
        2. Verifique se a planilha está acessível com as credenciais fornecidas
        """)
        return
    
    # ===== SIDEBAR - FILTROS =====
    with st.sidebar:
        st.markdown("### 🎯 Filtros")
        
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
        
        st.markdown("---")
        st.markdown("""
        <div style='padding: 16px; background-color: #F2F4F6; border-radius: 10px; margin-top: 24px;'>
            <p style='color: #6B7A8F; font-size: 0.85rem; margin: 0;'>
                📍 Dados atualizados em tempo real<br>
                🔄 Atualização automática a cada 5 minutos
            </p>
        </div>
        """, unsafe_allow_html=True)
    
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
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    
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
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== VISUALIZAÇÃO =====
    tab1, tab2 = st.tabs(["📋 Lista de Eventos", "📅 Visão Calendário"])
    
    with tab1:
        # Lista de eventos
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### Próximos Eventos")
        
        # Ordenar por data
        df_ordenado = df_filtrado.sort_values('Data início')
        
        for idx, row in df_ordenado.iterrows():
            color, tipo_class = get_event_color(row['Tipo de evento'])
            tag_class = get_event_tag_class(row['Tipo de evento'])
            
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
            
            st.markdown(f"""
            <div class="event-card {tipo_class}">
                <div style="margin-bottom: 8px;">
                    <span class="event-tag {tag_class}">{row['Tipo de evento']}</span>
                </div>
                <h3 style="margin: 8px 0; font-size: 1.1rem;">{row['Nome']}</h3>
                <div style="color: #6B7A8F; font-size: 0.9rem;">
                    📅 {data_inicio_str} até {data_fim_str}<br>
                    🎓 {row['Universidade']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        # Visão de calendário
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### Calendário de Eventos")
        
        # Selecionar mês para visualização
        col1, col2 = st.columns(2)
        with col1:
            ano_cal = st.selectbox("Ano", range(2024, 2027), index=1)
        with col2:
            mes_cal = st.selectbox("Mês", range(1, 13), 
                                   format_func=lambda x: calendar.month_name[x],
                                   index=datetime.now().month - 1)
        
        # Gerar calendário
        cal = calendar.monthcalendar(ano_cal, mes_cal)
        
        # Dias da semana
        dias_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        
        st.markdown("""
        <div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; margin-top: 16px;">
        """ + "".join([f"<div style='text-align: center; font-weight: 600; color: #3B4B5E; padding: 8px;'>{dia}</div>" 
                       for dia in dias_semana]) + "</div>", unsafe_allow_html=True)
        
        # Gerar grid do calendário
        calendario_html = "<div style='display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; margin-top: 8px;'>"
        
        hoje = datetime.now().date()
        
        for semana in cal:
            for dia in semana:
                if dia == 0:
                    calendario_html += "<div class='calendar-day' style='opacity: 0.3;'></div>"
                else:
                    data_dia = datetime(ano_cal, mes_cal, dia).date()
                    
                    # Verificar se há eventos neste dia
                    eventos_dia = df_filtrado[
                        (df_filtrado['Data início'].dt.date <= data_dia) &
                        (df_filtrado['Data Final'].dt.date >= data_dia)
                    ]
                    
                    classes = ['calendar-day']
                    if len(eventos_dia) > 0:
                        classes.append('has-event')
                    if data_dia == hoje:
                        classes.append('today')
                    
                    eventos_html = ""
                    for _, evento in eventos_dia.iterrows():
                        color, _ = get_event_color(evento['Tipo de evento'])
                        eventos_html += f"<div class='event-dot' style='background-color: {color};'></div>"
                    
                    calendario_html += f"""
                    <div class='{' '.join(classes)}'>
                        <div class='calendar-day-number'>{dia}</div>
                        <div>{eventos_html}</div>
                    </div>
                    """
        
        calendario_html += "</div>"
        st.markdown(calendario_html, unsafe_allow_html=True)
        
        # Legenda
        st.markdown("""
        <div style='margin-top: 24px; padding: 16px; background-color: #F2F4F6; border-radius: 10px;'>
            <strong>Legenda:</strong><br>
            <span style='display: inline-block; width: 12px; height: 12px; background-color: #FF6B8A; 
                         border-radius: 50%; margin: 4px 8px 4px 0;'></span> Feiras
            <span style='display: inline-block; width: 12px; height: 12px; background-color: #00D9FF; 
                         border-radius: 50%; margin: 4px 8px 4px 16px;'></span> Lives
            <span style='display: inline-block; width: 12px; height: 12px; background-color: #D4FF33; 
                         border-radius: 50%; margin: 4px 8px 4px 16px;'></span> Circles
            <span style='display: inline-block; width: 12px; height: 12px; background-color: #9E9E9E; 
                         border-radius: 50%; margin: 4px 8px 4px 16px;'></span> Outros
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #6B7A8F; padding: 24px 0;'>
        <strong>blūmi talents</strong> | Transformando a contratação de jovens talentos<br>
        <span style='font-size: 0.85rem;'>@blumi_talents</span>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

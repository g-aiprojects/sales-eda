import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import warnings
warnings.filterwarnings('ignore')

# ─── Настройки страницы ───────────────────────────────────────────
st.set_page_config(
    page_title="Анализ продаж 2022",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Стили ────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #F8FAFC; }
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }

    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem 1rem;
        text-align: center;
        border-left: 4px solid;
        box-shadow: 0 1px 8px rgba(0,0,0,0.06);
    }
    .kpi-value { font-size: 1.7rem; font-weight: 700; margin-bottom: 0.2rem; }
    .kpi-label { font-size: 0.78rem; color: #64748B; font-weight: 500; text-transform: uppercase; letter-spacing: 0.04em; }

    .section-title {
        font-size: 1.1rem; font-weight: 700; color: #1E293B;
        border-bottom: 2px solid #E2E8F0; padding-bottom: 0.4rem;
        margin-bottom: 1rem; margin-top: 1.5rem;
    }
    .insight-box {
        background: #EFF6FF; border-left: 4px solid #2563EB;
        border-radius: 0 8px 8px 0; padding: 0.8rem 1rem;
        margin: 0.5rem 0; font-size: 0.88rem; color: #1E3A5F;
    }
    .warning-box {
        background: #FEF2F2; border-left: 4px solid #EF4444;
        border-radius: 0 8px 8px 0; padding: 0.8rem 1rem;
        margin: 0.5rem 0; font-size: 0.88rem; color: #7F1D1D;
    }
</style>
""", unsafe_allow_html=True)

# ─── Загрузка данных ──────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel('Тест.xlsx')
    df['Бренд_ч']     = df['Бренд '].str.strip()
    df['Тип товара_ч'] = df['Тип товара '].str.strip()
    return df

df = load_data()

sales    = df[df['Проводка'] == 'Расход'].copy()
returns  = df[df['Проводка'] == 'Возврат'].copy()
df_sales = df[df['Проводка'].isin(['Расход','Возврат'])].copy()
sales_clean = sales[(sales['Рента'] >= 0) & (sales['Рента'] <= 1)].copy()

BG   = '#F8FAFC'
DARK = '#1E293B'
PALETTE = ['#2563EB','#7C3AED','#059669','#D97706','#DC2626',
           '#0891B2','#65A30D','#9333EA','#EA580C','#0284C7']

plt.rcParams['font.family']       = 'DejaVu Sans'
plt.rcParams['axes.spines.top']   = False
plt.rcParams['axes.spines.right'] = False

def fmt_mln(x):
    return f'{x/1e6:.1f} млн' if x >= 1e6 else f'{x/1e3:.0f} тыс'

# ─── Боковая панель — фильтры ─────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔽 Фильтры")

    all_cities   = sorted(sales['Город'].dropna().unique())
    all_curators = sorted(sales['Куратор'].dropna().unique())
    all_brands   = sorted(sales['Бренд_ч'].dropna().unique())

    sel_cities   = st.multiselect("Город", all_cities, default=all_cities)
    sel_curators = st.multiselect("Куратор", all_curators, default=all_curators)
    sel_brands   = st.multiselect("Бренд", all_brands, default=all_brands)

    st.markdown("---")
    st.markdown("**Период данных:** Февраль–Март 2022")
    st.markdown("**Источник:** Тест.xlsx")
    st.markdown("**Строк:** 18 717  |  **Столбцов:** 35")

# ─── Применяем фильтры ───────────────────────────────────────────
mask = (
    sales['Город'].isin(sel_cities) &
    sales['Куратор'].isin(sel_curators) &
    sales['Бренд_ч'].isin(sel_brands)
)
s  = sales[mask].copy()
sc = s[(s['Рента'] >= 0) & (s['Рента'] <= 1)].copy()
r  = returns[
    returns['Город'].isin(sel_cities) &
    returns['Куратор'].isin(sel_curators) &
    returns['Бренд_ч'].isin(sel_brands)
].copy()

# ─── Заголовок ────────────────────────────────────────────────────
st.markdown("# 📊 Анализ продаж — Февраль–Март 2022")
st.markdown("Интерактивный EDA-дашборд · Используй фильтры слева для сегментации")

# ─── KPI ─────────────────────────────────────────────────────────
gross   = s['Дельта'].sum()
ret_loss = r['Дельта'].sum()
net     = gross + ret_loss
leakage = abs(ret_loss) / gross * 100 if gross > 0 else 0

kpis = [
    ("Выручка",          f"{s['Сумма ИНФ'].sum()/1e6:.1f} млн ₸", "#2563EB"),
    ("Чистая прибыль",   f"{net/1e6:.1f} млн ₸",                  "#059669"),
    ("Потери возвратов", f"{leakage:.1f}%",                         "#DC2626"),
    ("Медианная маржа",  f"{sc['Рента'].median():.1%}" if len(sc)>0 else "—", "#7C3AED"),
    ("Клиентов",         f"{s['Клиент'].nunique():,}",              "#D97706"),
    ("Городов",          f"{s['Город'].nunique()}",                 "#0891B2"),
]

cols = st.columns(6)
for col, (label, val, color) in zip(cols, kpis):
    col.markdown(f"""
    <div class="kpi-card" style="border-left-color:{color}">
        <div class="kpi-value" style="color:{color}">{val}</div>
        <div class="kpi-label">{label}</div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Продажи", "🗺️ География", "🔄 Возвраты", "🏷️ ABC-анализ"
])

# ══════════════════════════════════════════════════════════════════
#  ТАБ 1 — ПРОДАЖИ
# ══════════════════════════════════════════════════════════════════
with tab1:
    col_l, col_r = st.columns(2)

    # Выручка по месяцам
    with col_l:
        st.markdown('<div class="section-title">Выручка по месяцам</div>', unsafe_allow_html=True)
        month_rev   = s.groupby('Месяц')['Сумма ИНФ'].sum()
        month_names = {2:'Февраль', 3:'Март', 4:'Апрель'}
        fig, ax = plt.subplots(figsize=(7, 4), facecolor=BG)
        ax.set_facecolor(BG)
        mlabels = [month_names.get(m, str(m)) for m in month_rev.index]
        bars = ax.bar(mlabels, month_rev.values/1e6, color=PALETTE[:len(mlabels)],
                      width=0.5, zorder=3)
        ax.set_ylabel('млн ₸'); ax.grid(axis='y', alpha=0.25, zorder=0)
        for bar, val in zip(bars, month_rev.values):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
                    fmt_mln(val), ha='center', va='bottom', fontsize=10, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig); plt.close()

    # Топ-10 кураторов
    with col_r:
        st.markdown('<div class="section-title">Топ-10 кураторов по выручке</div>', unsafe_allow_html=True)
        top_mgr = s.groupby('Куратор')['Сумма ИНФ'].sum().sort_values(ascending=True).tail(10)
        fig, ax = plt.subplots(figsize=(7, 4), facecolor=BG)
        ax.set_facecolor(BG)
        bars2 = ax.barh([n.replace(' МПП','') for n in top_mgr.index],
                        top_mgr.values/1e6, color=PALETTE[0], zorder=3)
        ax.set_xlabel('млн ₸'); ax.grid(axis='x', alpha=0.25, zorder=0)
        for bar, val in zip(bars2, top_mgr.values):
            ax.text(bar.get_width()+0.3, bar.get_y()+bar.get_height()/2,
                    fmt_mln(val), va='center', fontsize=8.5)
        plt.tight_layout()
        st.pyplot(fig); plt.close()

    # Scatter — матрица маржинальности
    st.markdown('<div class="section-title">Матрица маржинальности товаров</div>', unsafe_allow_html=True)
    model_data = (s.groupby('Модель').agg(
        Выручка=('Сумма ИНФ','sum'), Рента=('Рента','median'), Кол=('Кол плюс','sum'),
    ).dropna(subset=['Рента']).reset_index())
    model_data = model_data[(model_data['Рента']>0) & (model_data['Рента']<=1) &
                             (model_data['Выручка']>100_000)].copy()

    if len(model_data) > 5:
        x_med = model_data['Выручка'].median()
        y_med = model_data['Рента'].median()

        def quad(row):
            if   row['Выручка']>=x_med and row['Рента']>=y_med: return '#22C55E','Звезды'
            elif row['Выручка']>=x_med and row['Рента']<y_med:  return '#F59E0B','Дойные коровы'
            elif row['Выручка']<x_med  and row['Рента']>=y_med: return '#2563EB','Потенциал'
            else:                                                return '#EF4444','Аутсайдеры'

        model_data[['color','quad']] = model_data.apply(lambda r: pd.Series(quad(r)), axis=1)
        size = (model_data['Кол'] / model_data['Кол'].max() * 600).clip(lower=20)

        fig, ax = plt.subplots(figsize=(14, 6), facecolor=BG)
        ax.set_facecolor(BG)
        x_max = model_data['Выручка'].max()*1.1
        y_min = model_data['Рента'].min()*0.85
        y_max = model_data['Рента'].max()*1.1

        for (x0,x1,y0,y1,fc,tc,lbl) in [
            (0,x_med,y_med,y_max,'#EFF6FF','#2563EB','Потенциал'),
            (x_med,x_max,y_med,y_max,'#F0FDF4','#16A34A','Звезды'),
            (0,x_med,y_min,y_med,'#FEF2F2','#DC2626','Аутсайдеры'),
            (x_med,x_max,y_min,y_med,'#FFFBEB','#D97706','Дойные коровы'),
        ]:
            ax.fill_between([x0,x1], y0, y1, color=fc, alpha=0.55, zorder=1)
            ax.text((x0+x1)/2, y1-(y1-y0)*0.1, lbl, ha='center', va='top',
                    fontsize=9, color=tc, alpha=0.65, style='italic')

        ax.axvline(x_med, color='#94A3B8', linewidth=1.2, linestyle='--', alpha=0.5)
        ax.axhline(y_med, color='#94A3B8', linewidth=1.2, linestyle='--', alpha=0.5)
        ax.scatter(model_data['Выручка'], model_data['Рента'],
                   s=size, c=model_data['color'], alpha=0.75,
                   edgecolors='white', linewidth=0.8, zorder=4)

        top15 = model_data.nlargest(15,'Выручка')
        for _, row in top15.iterrows():
            lbl = row['Модель'].strip().lstrip('!').strip()[:18]
            txt = ax.annotate(lbl, xy=(row['Выручка'], row['Рента']),
                xytext=(6, 4), textcoords='offset points',
                fontsize=7, color=DARK, fontweight='bold', zorder=6)
            txt.set_path_effects([pe.withStroke(linewidth=2.5, foreground='white')])

        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'{v/1e6:.0f} млн'))
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
        ax.set_xlabel('Выручка (₸)', fontsize=11); ax.set_ylabel('Маржинальность (Рента)', fontsize=11)
        ax.set_xlim(left=0); ax.set_ylim(y_min, y_max); ax.grid(alpha=0.12, zorder=0)

        nS=(model_data['quad']=='Звезды').sum(); nC=(model_data['quad']=='Дойные коровы').sum()
        nP=(model_data['quad']=='Потенциал').sum(); nA=(model_data['quad']=='Аутсайдеры').sum()
        ax.legend(handles=[
            mpatches.Patch(color='#22C55E', label=f'Звезды ({nS})'),
            mpatches.Patch(color='#F59E0B', label=f'Дойные коровы ({nC})'),
            mpatches.Patch(color='#2563EB', label=f'Потенциал ({nP})'),
            mpatches.Patch(color='#EF4444', label=f'Аутсайдеры ({nA})'),
        ], loc='lower right', fontsize=9, framealpha=0.95)
        plt.tight_layout()
        st.pyplot(fig); plt.close()

        st.markdown(f"""
        <div class="insight-box">
        💡 <b>Медиана выручки:</b> {x_med/1e6:.1f} млн ₸ &nbsp;|&nbsp;
        <b>Медиана маржи:</b> {y_med:.1%} &nbsp;|&nbsp;
        <b>Размер пузыря</b> = объём продаж в штуках
        </div>""", unsafe_allow_html=True)
    else:
        st.info("Недостаточно данных для scatter-графика при текущих фильтрах")

    # Boxplot маржи по кураторам
    st.markdown('<div class="section-title">Разброс маржинальности по кураторам</div>', unsafe_allow_html=True)
    if len(sc) > 10:
        mgr_ord  = sc.groupby('Куратор')['Рента'].median().sort_values(ascending=False)
        top_mgrs = mgr_ord.head(10).index.tolist()
        data_box = [sc[sc['Куратор']==m]['Рента'].values for m in top_mgrs]
        short_m  = [n.replace(' МПП','') for n in top_mgrs]
        fig, ax = plt.subplots(figsize=(14, 4), facecolor=BG)
        ax.set_facecolor(BG)
        bp = ax.boxplot(data_box, labels=short_m, patch_artist=True,
                        medianprops={'color':'white','linewidth':2})
        for i, patch in enumerate(bp['boxes']):
            patch.set_facecolor(PALETTE[i % len(PALETTE)]); patch.set_alpha(0.8)
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
        ax.grid(axis='y', alpha=0.25); ax.set_ylabel('Рента')
        plt.tight_layout()
        st.pyplot(fig); plt.close()

# ══════════════════════════════════════════════════════════════════
#  ТАБ 2 — ГЕОГРАФИЯ
# ══════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">Выручка и маржинальность по городам</div>', unsafe_allow_html=True)

    geo = (s.groupby('Город').agg(
        Выручка=('Сумма ИНФ','sum'), Прибыль=('Дельта','sum'), Рента=('Рента','median')
    ).reset_index())
    geo = geo[geo['Рента'].between(0,1)].copy()
    geo['Маржа'] = geo['Прибыль'] / geo['Выручка']
    geo = geo[(geo['Город'] != 'ТАРАЗ') & (geo['Выручка'] > 200_000)]
    geo = geo.sort_values('Выручка', ascending=True).tail(20)

    if len(geo) > 0:
        margin_med = geo['Маржа'].median()
        norm_g = mcolors.Normalize(vmin=geo['Маржа'].min(), vmax=geo['Маржа'].max())
        cols_g = [cm.Blues(norm_g(m)*0.6+0.35) for m in geo['Маржа']]

        fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(14, 7), facecolor=BG,
                                           gridspec_kw={'wspace':0.05})
        bars_l = ax_l.barh(geo['Город'], geo['Выручка']/1e6, color=cols_g,
                           height=0.65, zorder=3, edgecolor='white', linewidth=0.5)
        ax_l.set_facecolor(BG); ax_l.set_xlabel('Выручка (млн ₸)', fontsize=10)
        ax_l.set_title('Выручка\n(темнее = выше маржа)', fontsize=11, fontweight='bold', pad=8, color=DARK)
        ax_l.grid(axis='x', alpha=0.2, zorder=0)
        for bar, val in zip(bars_l, geo['Выручка']):
            ax_l.text(bar.get_width()+0.3, bar.get_y()+bar.get_height()/2,
                      f'{val/1e6:.1f}', va='center', fontsize=8)

        bars_r = ax_r.barh(geo['Город'], geo['Маржа']*100, color=cols_g,
                           height=0.65, zorder=3, edgecolor='white', linewidth=0.5)
        ax_r.axvline(margin_med*100, color='#DC2626', linewidth=1.5, linestyle='--',
                     label=f'Медиана {margin_med:.1%}')
        ax_r.set_facecolor(BG); ax_r.set_xlabel('Маржа (%)', fontsize=10)
        ax_r.set_title('Маржинальность\n(Прибыль / Выручка)', fontsize=11, fontweight='bold', pad=8, color=DARK)
        ax_r.set_yticklabels([]); ax_r.grid(axis='x', alpha=0.2, zorder=0)
        ax_r.legend(fontsize=9, loc='lower right')
        for bar, val in zip(bars_r, geo['Маржа']):
            ax_r.text(bar.get_width()+0.3, bar.get_y()+bar.get_height()/2,
                      f'{val:.1%}', va='center', fontsize=8)

        sm = plt.cm.ScalarMappable(cmap=cm.Blues,
             norm=mcolors.Normalize(vmin=geo['Маржа'].min()*100, vmax=geo['Маржа'].max()*100))
        sm.set_array([])
        fig.colorbar(sm, ax=ax_r, shrink=0.5, pad=0.02, label='Маржа (%)')
        plt.savefig('/tmp/geo_tmp.png', dpi=120, bbox_inches='tight', facecolor=BG)
        st.pyplot(fig); plt.close()

        st.markdown(f"""
        <div class="warning-box">
        ⚠️ <b>Тараз исключён</b> как статистический выброс (маржа 86% при выручке 3.4 млн ₸ — нерепрезентативная выборка)
        </div>""", unsafe_allow_html=True)

        # Таблица
        st.markdown('<div class="section-title">Детальная таблица по городам</div>', unsafe_allow_html=True)
        geo_table = geo.sort_values('Выручка', ascending=False).copy()
        geo_table['Выручка (млн)']   = (geo_table['Выручка']/1e6).round(1)
        geo_table['Прибыль (млн)']   = (geo_table['Прибыль']/1e6).round(1)
        geo_table['Маржа %']         = (geo_table['Маржа']*100).round(1)
        st.dataframe(geo_table[['Город','Выручка (млн)','Прибыль (млн)','Маржа %']]
                     .reset_index(drop=True), use_container_width=True)

# ══════════════════════════════════════════════════════════════════
#  ТАБ 3 — ВОЗВРАТЫ
# ══════════════════════════════════════════════════════════════════
with tab3:
    gross_p  = s['Дельта'].sum()
    ret_l    = r['Дельта'].sum()
    leak_pct = abs(ret_l)/gross_p*100 if gross_p > 0 else 0

    st.markdown(f"""
    <div class="warning-box">
    ⚠️ Возвраты съедают <b>{leak_pct:.1f}%</b> валовой прибыли &nbsp;|&nbsp;
    Убыток: <b>{ret_l/1e6:.2f} млн ₸</b>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">По брендам</div>', unsafe_allow_html=True)
        ret_brand = r.groupby('Бренд_ч')['Дельта'].sum().sort_values().head(10)
        ret_brand = ret_brand[ret_brand < 0]
        if len(ret_brand) > 0:
            fig, ax = plt.subplots(figsize=(7, 5), facecolor=BG)
            ax.set_facecolor(BG)
            pal_r = plt.cm.Reds_r(np.linspace(0.3, 0.85, len(ret_brand)))
            bars_rb = ax.barh(ret_brand.index, ret_brand.values/1e6, color=pal_r,
                              height=0.65, zorder=3, edgecolor='white', linewidth=0.5)
            ax.set_xlabel('Убыток (млн ₸)', fontsize=10)
            ax.grid(axis='x', alpha=0.25, zorder=0)
            for bar, val in zip(bars_rb, ret_brand.values):
                ax.text(bar.get_width()-0.02, bar.get_y()+bar.get_height()/2,
                        f'{val/1e6:.2f}', va='center', ha='right', fontsize=8,
                        color='white', fontweight='bold')
            plt.tight_layout(); st.pyplot(fig); plt.close()

    with col2:
        st.markdown('<div class="section-title">По складам</div>', unsafe_allow_html=True)
        ret_sklad = r.groupby('Склад')['Дельта'].sum().sort_values()
        ret_sklad = ret_sklad[ret_sklad < 0]
        if len(ret_sklad) > 0:
            fig, ax = plt.subplots(figsize=(7, 5), facecolor=BG)
            ax.set_facecolor(BG)
            slab  = [s_.replace('СКЛАД ','') for s_ in ret_sklad.index]
            svals = ret_sklad.abs().values
            explode = [0.08] + [0.03]*(len(svals)-1)
            wedge_colors = ['#EF4444','#F97316','#FBBF24','#A3A3A3'][:len(svals)]
            _, _, autotexts = ax.pie(svals, labels=None, autopct='%1.1f%%',
                startangle=120, colors=wedge_colors, explode=explode,
                wedgeprops={'width':0.55,'edgecolor':'white','linewidth':2},
                pctdistance=0.78)
            for at in autotexts:
                at.set_fontsize(10); at.set_fontweight('bold'); at.set_color('white')
            ax.legend([f'{l}  ({v/1e6:.1f} млн)' for l,v in zip(slab, svals)],
                      loc='lower center', bbox_to_anchor=(0.5,-0.12), fontsize=8)
            plt.tight_layout(); st.pyplot(fig); plt.close()

    st.markdown('<div class="section-title">По типу товара</div>', unsafe_allow_html=True)
    ret_type = r.groupby('Тип товара_ч')['Дельта'].sum().sort_values().head(10)
    ret_type = ret_type[ret_type < 0]
    if len(ret_type) > 0:
        fig, ax = plt.subplots(figsize=(14, 4), facecolor=BG)
        ax.set_facecolor(BG)
        pal_t = plt.cm.Oranges_r(np.linspace(0.3, 0.85, len(ret_type)))
        bars_rt = ax.barh(ret_type.index, ret_type.values/1e6, color=pal_t,
                          height=0.55, zorder=3, edgecolor='white', linewidth=0.5)
        ax.set_xlabel('Убыток (млн ₸)', fontsize=10)
        ax.grid(axis='x', alpha=0.25, zorder=0)
        for bar, val in zip(bars_rt, ret_type.values):
            ax.text(bar.get_width()-0.02, bar.get_y()+bar.get_height()/2,
                    f'{val/1e6:.2f}', va='center', ha='right', fontsize=8,
                    color='white', fontweight='bold')
        plt.tight_layout(); st.pyplot(fig); plt.close()

# ══════════════════════════════════════════════════════════════════
#  ТАБ 4 — ABC-АНАЛИЗ
# ══════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">ABC-анализ брендов по чистой прибыли (Дельта)</div>',
                unsafe_allow_html=True)

    ds = df_sales[
        df_sales['Город'].isin(sel_cities) &
        df_sales['Куратор'].isin(sel_curators) &
        df_sales['Бренд_ч'].isin(sel_brands)
    ]
    abc = (ds.groupby('Бренд_ч')['Дельта'].sum()
           .sort_values(ascending=False).reset_index())
    total_p = abc['Дельта'].sum()
    abc['Share']      = abc['Дельта'] / total_p * 100
    abc['Cumulative'] = abc['Share'].cumsum()
    abc['Group']      = abc['Cumulative'].apply(
        lambda c: 'A' if c<=80 else ('B' if c<=95 else 'C'))

    cols_abc = {'A':'#22C55E','B':'#F59E0B','C':'#EF4444'}
    x_abc    = np.arange(len(abc))

    fig, ax_abc = plt.subplots(figsize=(16, 6), facecolor=BG)
    fig.subplots_adjust(bottom=0.30)
    ax_abc.set_facecolor(BG)
    ax_abc.bar(x_abc, abc['Дельта'], color=[cols_abc[g] for g in abc['Group']],
               width=0.65, zorder=3, edgecolor='white', linewidth=0.8)
    ax_abc.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f'{v/1e6:.0f} млн'))
    ax_abc.set_ylabel('Дельта (прибыль), ₸', fontsize=10)
    ax_abc.grid(axis='y', alpha=0.25, zorder=0)
    ax_abc.set_xticks(x_abc)
    ax_abc.set_xticklabels(abc['Бренд_ч'], rotation=45, ha='right', va='top', fontsize=8)

    ax2_abc = ax_abc.twinx()
    ax2_abc.plot(x_abc, abc['Cumulative'], color=DARK, marker='o', markersize=4,
                 linewidth=2, zorder=5)
    ax2_abc.set_ylim(0, 112); ax2_abc.set_ylabel('Накопленный итог (%)', fontsize=10)
    ax2_abc.axhline(80, color='#22C55E', linestyle='--', linewidth=1.2, alpha=0.7)
    ax2_abc.axhline(95, color='#F59E0B', linestyle='--', linewidth=1.2, alpha=0.7)
    ax2_abc.text(len(abc)-1, 81.5, '80%', color='#22C55E', fontsize=8, ha='right')
    ax2_abc.text(len(abc)-1, 96.5, '95%', color='#F59E0B', fontsize=8, ha='right')
    ax2_abc.spines['top'].set_visible(False)

    nA=(abc['Group']=='A').sum(); nB=(abc['Group']=='B').sum(); nC=(abc['Group']=='C').sum()
    ax_abc.legend(handles=[
        mpatches.Patch(color='#22C55E', label=f'A — 80% прибыли ({nA} брендов)'),
        mpatches.Patch(color='#F59E0B', label=f'B — до 95% ({nB} брендов)'),
        mpatches.Patch(color='#EF4444', label=f'C — хвост ({nC} брендов)'),
    ], loc='upper right', bbox_to_anchor=(1.0, 0.92), fontsize=9, framealpha=0.95)

    st.pyplot(fig); plt.close()

    # Таблица ABC
    st.markdown('<div class="section-title">Таблица ABC-групп</div>', unsafe_allow_html=True)
    abc_tbl = abc.copy()
    abc_tbl['Дельта (млн)'] = (abc_tbl['Дельта']/1e6).round(2)
    abc_tbl['Доля %']       = abc_tbl['Share'].round(1)
    abc_tbl['Накопл. %']    = abc_tbl['Cumulative'].round(1)
    st.dataframe(
        abc_tbl[['Бренд_ч','Дельта (млн)','Доля %','Накопл. %','Group']]
        .rename(columns={'Бренд_ч':'Бренд','Group':'Группа'})
        .reset_index(drop=True),
        use_container_width=True
    )

# ─── Футер ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#94A3B8; font-size:0.8rem'>"
    "EDA · Анализ продаж Февраль–Март 2022 · Тестовое задание дата-аналитика"
    "</div>", unsafe_allow_html=True)

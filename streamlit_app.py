import streamlit as st
import pandas as pd
import math

# 1. 페이지 설정
st.set_page_config(page_title="TSEI 고분자-용매 DB 계산기", page_icon="🧪", layout="wide")

# 2. 데이터 로드 함수
@st.cache_data
def load_db():
    try:
        # 업로드된 CSV 파일 읽기 (인코딩 문제 방지를 위해 utf-8-sig 사용)
        solv_df = pd.read_csv("용매_데이터.csv", encoding='utf-8-sig')
        poly_df = pd.read_csv("고분자_데이터.csv", encoding='utf-8-sig')
        return solv_df, poly_df
    except FileNotFoundError:
        return None, None

solv_db, poly_db = load_db()

st.title("🧪 고분자-용매 특성 DB 및 정밀 계산기")

# 3. 사이드바: 환경 설정
with st.sidebar:
    st.header("⚙️ 환경 설정")
    temp = st.slider("실험실 온도 (°C)", min_value=0.0, max_value=40.0, value=25.0, step=0.1)
    molar_volume = 22.4 * (273.15 + temp) / 273.15
    st.write(f"현재 온도 몰부피: **{molar_volume:.3f} L/mol**")
    st.divider()
    if st.button("🔄 DB 다시 불러오기"):
        st.cache_data.clear()
        st.rerun()

# 4. 메인 섹션: DB 검색
st.header("🔍 고분자/용매 특성 검색")
tab1, tab2 = st.tabs(["💧 용매 (Solvent) DB", "🧬 고분자 (Polymer) DB"])

selected_solv_data = None

with tab1:
    if solv_db is not None:
        search_solv = st.selectbox("용매를 선택하세요", ["직접 입력"] + solv_db["용매명"].tolist())
        if search_solv != "직접 입력":
            selected_solv_data = solv_db[solv_db["용매명"] == search_solv].iloc[0]
            
            # 용매 정보 표시
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("분자량", f"{selected_solv_data['분자량 (g/mol)']} g/mol")
            c2.metric("밀도", f"{selected_solv_data['밀도 (g/cm3)']} g/cm³")
            c3.metric("끓는점", f"{selected_solv_data['끓는점 (℃)']} ℃")
            c4.metric("인화점", f"{selected_solv_data['인화점 (℃)']} ℃")
            
            st.warning(f"⚠️ **위험성 (GHS)**: {selected_solv_data['위험성 (GHS) / 관리']}")
            st.info(f"📝 **비고**: {selected_solv_data['비고']}")
    else:
        st.error("저장소에서 '용매_데이터.csv'를 찾을 수 없습니다.")

with tab2:
    if poly_db is not None:
        search_poly = st.selectbox("고분자를 선택하세요", poly_db["고분자명"].tolist())
        selected_poly = poly_db[poly_db["고분자명"] == search_poly].iloc[0]
        
        col_p1, col_p2 = st.columns([1, 2])
        with col_p1:
            st.write(f"**약어 (Abbr.)**: {selected_poly['Abbreviation']}")
            st.write(f"**밀도**: {selected_poly['Density (g/cm3)']} g/cm³")
            st.write(f"**용해도 파라미터**: {selected_poly['Solubility Parameter (cal/cm3)1/2']}")
        with col_p2:
            st.write(f"**구조/특징**: {selected_poly['Structure']}")
            st.write(f"**특이사항**: {selected_poly['특이사항']}")
    else:
        st.error("저장소에서 '고분자_데이터.csv'를 찾을 수 없습니다.")

st.divider()

# 5. 계산기 섹션 (DB 연동)
st.header("📊 PPM 주입량 계산기")

# DB 선택 여부에 따라 기본값 자동 설정
def_name = selected_solv_data["용매명"] if selected_solv_data is not None else "Water"
def_mw = float(selected_solv_data["분자량 (g/mol)"]) if selected_solv_data is not None else 18.015
def_dens = float(selected_solv_data["밀도 (g/cm3)"]) if selected_solv_data is not None else 1.000
def_bp = str(selected_solv_data["끓는점 (℃)"]) if selected_solv_data is not None else "100.0"

col_calc1, col_calc2, col_calc3 = st.columns(3)
with col_calc1:
    calc_name = st.text_input("성분명", value=def_name)
    mw = st.number_input("분자량 (g/mol)", value=def_mw, format="%.3f")
with col_calc2:
    air_vol = st.number_input("Air 주입량 (L)", value=12.0)
    density = st.number_input("밀도 (g/cm³)", value=def_dens, format="%.3f")
with col_calc3:
    target_ppm = st.number_input("목표 농도 (PPM)", value=1000.0)
    purity = st.number_input("순도 (%)", value=100.0)

# 주입량 계산
req_ul = (target_ppm * mw * air_vol) / (molar_volume * density * (purity/100) * 1000)

# 결과 출력
res_c, tool_c = st.columns(2)
with res_c:
    st.markdown(f"""
    <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; border-left: 5px solid #ff4b4b;">
        <p style="margin:0;">필요한 <b>{calc_name}</b> 총 주입량</p>
        <h1 style="color:#ff4b4b; margin-top:0;">{req_ul:.2f} μL</h1>
    </div>
    """, unsafe_allow_html=True)

with tool_c:
    st.markdown("### 🛠️ 도구 가이드")
    if req_ul <= 10:
        st.warning(f"📍 **추천:** 마이크로 실린지 (눈금: **{req_ul:.2f}**)")
    elif req_ul <= 100:
        st.success(f"📍 **추천:** 마이크로 피펫 (**{req_ul:.1f} μL** × 1회)")
    else:
        num = math.ceil(req_ul / 100)
        vol = req_ul / num
        st.success(f"📍 **추천:** 피펫 분할 주입 (세팅: **{vol:.1f} μL** / 횟수: **{num}번**)")

# 공식 안내
with st.expander("📝 계산 공식 보기"):
    st.latex(r"V_{liq}(\mu L) = \frac{PPM \times MW(g/mol) \times V_{air}(L)}{V_m(L/mol) \times \rho(g/mL) \times (Purity/100) \times 1000}")
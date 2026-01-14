import streamlit as st
import pandas as pd
import math

# 1. 페이지 설정
st.set_page_config(page_title="TSEI 고분자-용매 통합 시스템", page_icon="🧪", layout="wide")

# 2. 엑셀 데이터 로드 함수 (시트별로 불러오기)
@st.cache_data
def load_excel_data():
    file_name = "고분자-용매 특성표.xlsx"
    try:
        # 시트 이름에 맞춰 데이터 로드 (헤더 위치에 따라 skiprows 조정 가능)
        solv_df = pd.read_excel(file_name, sheet_name="용매 특성 요약", skiprows=3)
        poly_df = pd.read_excel(file_name, sheet_name="고분자 18종 특성 요약", skiprows=3)
        hydro_df = pd.read_excel(file_name, sheet_name="Sheet2", skiprows=1)
        return solv_df, poly_df, hydro_df
    except Exception as e:
        st.error(f"엑셀 파일을 찾을 수 없거나 시트 이름이 일치하지 않습니다: {e}")
        return None, None, None

solv_db, poly_db, hydro_db = load_excel_data()

st.title("🧪 TSEI 고분자-용매 통합 DB & 계산기")

# 3. 환경 설정 사이드바
with st.sidebar:
    st.header("⚙️ 실험 환경 설정")
    temp = st.slider("실험실 온도 (°C)", 0.0, 40.0, 25.0, 0.1)
    molar_volume = 22.4 * (273.15 + temp) / 273.15
    st.write(f"현재 온도 몰부피: **{molar_volume:.3f} L/mol**")
    st.divider()
    if st.button("🔄 데이터 새로고침"):
        st.cache_data.clear()
        st.rerun()

# 4. 정보 조회 섹션 (탭 구성)
st.header("🔍 데이터베이스 검색")
tab1, tab2, tab3 = st.tabs(["💧 용매 특성 요약", "🧬 고분자 18종 특성", "🌊 용매 친수성 (Sheet2)"])

selected_solv_from_db = None

with tab1:
    if solv_db is not None:
        # 용매 선택 (selectbox)
        solv_list = solv_db["용매명"].dropna().tolist()
        choice_solv = st.selectbox("조회할 용매를 선택하세요", ["선택 안 함"] + solv_list)
        
        if choice_solv != "선택 안 함":
            selected_solv_from_db = solv_db[solv_db["용매명"] == choice_solv].iloc[0]
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("분자량 (Mw)", f"{selected_solv_from_db['분자량 (g/mol)']} g/mol")
            c2.metric("밀도 (Density)", f"{selected_solv_from_db['밀도 (g/cm3)']} g/cm³")
            c3.metric("끓는점 (B.P)", f"{selected_solv_from_db['끓는점 (℃)']} ℃")
            c4.metric("인화점 (F.P)", f"{selected_solv_from_db['인화점 (℃)']} ℃")
            
            st.warning(f"⚠️ **위험성 (GHS)**: {selected_solv_from_db['위험성 (GHS) / 관리']}")
            st.info(f"📝 **비고**: {selected_solv_from_db['비고']}")

with tab2:
    if poly_db is not None:
        poly_list = poly_db["고분자명"].dropna().tolist()
        choice_poly = st.selectbox("조회할 고분자를 선택하세요", poly_list)
        p_data = poly_db[poly_db["고분자명"] == choice_poly].iloc[0]
        
        pc1, pc2 = st.columns([1, 2])
        with pc1:
            st.write(f"**약어 (Abbr.)**: {p_data['Abbreviation']}")
            st.write(f"**밀도**: {p_data['Density (g/cm3)']} g/cm³")
            st.write(f"**용해도 파라미터**: {p_data['Solubility Parameter (cal/cm3)1/2']}")
        with pc2:
            st.write(f"**구조/특징**: {p_data['Structure']}")
            st.write(f"**특이사항**: {p_data['특이사항']}")

with tab3:
    if hydro_db is not None:
        st.write("### 용매별 친수성 및 특성 상세 (Sheet2)")
        st.dataframe(hydro_db, use_container_width=True)

st.divider()

# 5. PPM 계산기 섹션 (DB 연동)
st.header("📊 정밀 주입량 계산기")

# DB에서 선택된 값이 있으면 기본값으로 자동 입력
def_name = selected_solv_from_db["용매명"] if selected_solv_from_db is not None else ""
def_mw = float(selected_solv_from_db["분자량 (g/mol)"]) if selected_solv_from_db is not None else 0.0
def_dens = float(selected_solv_from_db["밀도 (g/cm3)"]) if selected_solv_from_db is not None else 1.0

col_a, col_b, col_c = st.columns(3)
with col_a:
    calc_name = st.text_input("성분명", value=def_name)
    mw = st.number_input("분자량 (g/mol)", value=def_mw, format="%.3f")
with col_b:
    air_vol = st.number_input("Air 주입량 (L)", value=12.0)
    density = st.number_input("밀도 (g/cm³)", value=def_dens, format="%.3f")
with col_c:
    target_ppm = st.number_input("목표 농도 (PPM)", value=1000.0)
    purity = st.number_input("순도 (%)", value=100.0)

# 주입량 계산 공식 적용
if mw > 0 and density > 0:
    req_ul = (target_ppm * mw * air_vol) / (molar_volume * density * (purity/100) * 1000)
else:
    req_ul = 0.0

# 6. 계산 결과 및 스마트 도구 가이드
res_col, tool_col = st.columns(2)

with res_col:
    st.markdown(f"""
    <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; border-left: 5px solid #ff4b4b;">
        <p style="margin:0; font-size:16px;">필요한 <b>{calc_name}</b> 총 주입량</p>
        <h1 style="color:#ff4b4b; margin-top:0;">{req_ul:.2f} μL</h1>
    </div>
    """, unsafe_allow_html=True)

with tool_col:
    st.markdown("### 🛠️ 추천 도구 및 사용법")
    
    if req_ul <= 0:
        st.write("성분 정보를 입력하면 계산 결과가 표시됩니다.")
    elif req_ul <= 10:
        st.warning("📍 **추천 도구: 마이크로 실린지 (10μL)**")
        st.write(f"눈금을 **{req_ul:.2f}**에 맞춰 1회 주입하세요.")
    elif req_ul <= 100:
        st.success("📍 **추천 도구: 마이크로 피펫 (100μL)**")
        st.markdown(f"**{req_ul:.1f} μL**를 설정하여 1회 주입하세요.")
    else:
        # 100μL 이상일 때 분할 주입 로직
        num_injections = math.ceil(req_ul / 100)
        vol_per_time = req_ul / num_injections
        st.success(f"📍 **추천 도구: 마이크로 피펫 (100μL) - {num_injections}회 분할**")
        st.markdown(f"""
        <div style="background-color:#e8f4ea; padding:15px; border-radius:10px; border: 1px solid #28a745;">
            <p style="margin:0; color:#1e7e34;"><b>피펫 세팅:</b> {vol_per_time:.1f} μL</p>
            <p style="margin:0; color:#1e7e34;"><b>주입 횟수:</b> {num_injections}번 나누어 주입</p>
        </div>
        """, unsafe_allow_html=True)

# 7. MSDS 검색 링크 버튼
if calc_name:
    st.divider()
    st.link_button(f"🌐 {calc_name} 상세 MSDS 검색", f"https://pubchem.ncbi.nlm.nih.gov/#query={calc_name}")
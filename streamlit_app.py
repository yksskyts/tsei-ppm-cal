import streamlit as st
import pandas as pd
import math

# 1. 페이지 설정
st.set_page_config(page_title="TSEI 통합 연구 지원 시스템 V2", page_icon="🧪", layout="wide")

# --- [내장 데이터베이스 구축] ---

# 1. 용매 종합 DB (보내주신 엑셀 시트 23종 전체 반영)
SOLVENT_DB = [
    {"용매명": "Acetone", "Mw": 58.08, "Density": 0.791, "BP": 56.1, "FP": -20.0, "인화성": "매우 높음", "GHS": "🔥 인화성, ⚠️ 자극성", "특이사항": "휘발성 강함", "친수성": "보통"},
    {"용매명": "Acetonitrile", "Mw": 41.05, "Density": 0.786, "BP": 81.6, "FP": 2.0, "인화성": "높음", "GHS": "🔥 인화성, 💀 독성", "특이사항": "피부 흡수 주의", "친수성": "높음"},
    {"용매명": "Benzene", "Mw": 78.11, "Density": 0.876, "BP": 80.1, "FP": -11.1, "인화성": "매우 높음", "GHS": "🔥 인화성, ☣️ 발암성", "특이사항": "1급 발암물질 사용엄금", "친수성": "매우 낮음"},
    {"용매명": "Carbon tetrachloride", "Mw": 153.82, "Density": 1.594, "BP": 76.7, "FP": "N/A", "인화성": "없음", "GHS": "💀 독성, ☣️ 발암성", "특이사항": "오존층 파괴물질", "친수성": "매우 낮음"},
    {"용매명": "Chloroform", "Mw": 119.38, "Density": 1.483, "BP": 61.2, "FP": "N/A", "인화성": "없음", "GHS": "💀 독성, ☣️ 발암성", "특이사항": "마취성 주의", "친수성": "낮음"},
    {"용매명": "Cyclohexane", "Mw": 84.16, "Density": 0.778, "BP": 80.7, "FP": -20.0, "인화성": "매우 높음", "GHS": "🔥 인화성, ⚠️ 자극성", "특이사항": "흡입 주의", "친수성": "매우 낮음"},
    {"용매명": "1,2-Dichloroethane", "Mw": 98.96, "Density": 1.253, "BP": 83.5, "FP": 13.0, "인화성": "높음", "GHS": "🔥 인화성, 💀 독성", "특이사항": "간 손상 주의", "친수성": "낮음"},
    {"용매명": "Dichloromethane (MC)", "Mw": 84.93, "Density": 1.326, "BP": 39.6, "FP": "N/A", "인화성": "없음", "GHS": "💀 독성, ☣️ 발암성", "특이사항": "증기압 매우 높음", "친수성": "낮음"},
    {"용매명": "Diethyl ether", "Mw": 74.12, "Density": 0.713, "BP": 34.6, "FP": -45.0, "인화성": "매우 높음", "GHS": "🔥 인화성, ⚠️ 자극성", "특이사항": "폭발성 과산화물 형성", "친수성": "낮음"},
    {"용매명": "N,N-Dimethylformamide (DMF)", "Mw": 73.09, "Density": 0.944, "BP": 153.0, "FP": 58.0, "인화성": "보통", "GHS": "💀 독성, ⚠️ 생식독성", "특이사항": "피부 흡수 주의", "친수성": "높음"},
    {"용매명": "1,4-Dioxane", "Mw": 88.11, "Density": 1.033, "BP": 101.1, "FP": 12.0, "인화성": "높음", "GHS": "🔥 인화성, ☣️ 발암성", "특이사항": "장기 손상 주의", "친수성": "높음"},
    {"용매명": "Ethanol", "Mw": 46.07, "Density": 0.789, "BP": 78.4, "FP": 13.0, "인화성": "높음", "GHS": "🔥 인화성, ⚠️ 자극성", "특이사항": "화기 엄금", "친수성": "높음"},
    {"용매명": "Ethyl acetate", "Mw": 88.11, "Density": 0.902, "BP": 77.1, "FP": -4.0, "인화성": "높음", "GHS": "🔥 인화성, ⚠️ 자극성", "특이사항": "과일향, 환기 주의", "친수성": "보통"},
    {"용매명": "n-Heptane", "Mw": 100.21, "Density": 0.684, "BP": 98.4, "FP": -4.0, "인화성": "높음", "GHS": "🔥 인화성, ⚠️ 자극성", "특이사항": "환경 유해 주의", "친수성": "매우 낮음"},
    {"용매명": "n-Hexane", "Mw": 86.18, "Density": 0.655, "BP": 69.0, "FP": -22.0, "인화성": "매우 높음", "GHS": "🔥 인화성, 💀 독성", "특이사항": "말초신경 마비 주의", "친수성": "매우 낮음"},
    {"용매명": "Methanol", "Mw": 32.04, "Density": 0.792, "BP": 64.7, "FP": 11.0, "인화성": "높음", "GHS": "🔥 인화성, 💀 독성", "특이사항": "실명 위협 독성", "친수성": "높음"},
    {"용매명": "n-Pentane", "Mw": 72.15, "Density": 0.626, "BP": 36.1, "FP": -49.0, "인화성": "매우 높음", "GHS": "🔥 인화성, ⚠️ 자극성", "특이사항": "초저온 보관 권장", "친수성": "매우 낮음"},
    {"용매명": "1-Propanol", "Mw": 60.1, "Density": 0.803, "BP": 97.2, "FP": 15.0, "인화성": "높음", "GHS": "🔥 인화성, ⚠️ 자극성", "특이사항": "눈 손상 주의", "친수성": "높음"},
    {"용매명": "2-Propanol (IPA)", "Mw": 60.1, "Density": 0.786, "BP": 82.6, "FP": 12.0, "인화성": "높음", "GHS": "🔥 인화성, ⚠️ 자극성", "특이사항": "살균용 알코올 냄새", "친수성": "보통"},
    {"용매명": "Tetrahydrofuran (THF)", "Mw": 72.11, "Density": 0.889, "BP": 66.0, "FP": -14.0, "인화성": "매우 높음", "GHS": "🔥 인화성, ⚠️ 자극성", "특이사항": "장기 보관 시 폭발성", "친수성": "보통"},
    {"용매명": "Toluene", "Mw": 92.14, "Density": 0.867, "BP": 110.6, "FP": 4.4, "인화성": "높음", "GHS": "🔥 인화성, 💀 독성", "특이사항": "생식독성 주의", "친수성": "낮음"},
    {"용매명": "Water", "Mw": 18.02, "Density": 1.0, "BP": 100.0, "FP": "N/A", "인화성": "없음", "GHS": "✅ 안전", "특이사항": "전기 기구 주의", "친수성": "매우 높음"},
    {"용매명": "NMP", "Mw": 99.13, "Density": 1.028, "BP": 202.0, "FP": 91.0, "인화성": "낮음", "GHS": "⚠️ 생식독성, 자극성", "특이사항": "고온 작업 주의", "친수성": "높음"}
]

# 2. 고분자 종합 DB (보내주신 엑셀 시트 18종 전체 반영)
POLYMER_DB = [
    {"고분자명": "High Density Polyethylene", "Abbr": "HDPE", "Density": 0.95, "Sol_Param": 8.0, "Structure": "Linear"},
    {"고분자명": "Low Density Polyethylene", "Abbr": "LDPE", "Density": 0.92, "Sol_Param": 7.9, "Structure": "Branched"},
    {"고분자명": "Polypropylene", "Abbr": "PP", "Density": 0.90, "Sol_Param": 8.1, "Structure": "Isotactic"},
    {"고분자명": "Polystyrene", "Abbr": "PS", "Density": 1.05, "Sol_Param": 9.1, "Structure": "Amorphous"},
    {"고분자명": "Poly(methyl methacrylate)", "Abbr": "PMMA", "Density": 1.18, "Sol_Param": 9.3, "Structure": "Glassy"},
    {"고분자명": "Poly(vinyl chloride)", "Abbr": "PVC", "Density": 1.39, "Sol_Param": 9.6, "Structure": "Rigid/Flexible"},
    {"고분자명": "Poly(ethylene terephthalate)", "Abbr": "PET", "Density": 1.37, "Sol_Param": 10.7, "Structure": "Semi-crystalline"},
    {"고분자명": "Polyamide 6 (Nylon 6)", "Abbr": "PA 6", "Density": 1.14, "Sol_Param": 13.6, "Structure": "Hydrogen bonded"},
    {"고분자명": "Polyamide 66 (Nylon 66)", "Abbr": "PA 66", "Density": 1.14, "Sol_Param": 13.6, "Structure": "Hydrogen bonded"},
    {"고분자명": "Polycarbonate", "Abbr": "PC", "Density": 1.20, "Sol_Param": 9.8, "Structure": "Engineering plastic"},
    {"고분자명": "Poly(butylene terephthalate)", "Abbr": "PBT", "Density": 1.31, "Sol_Param": 10.8, "Structure": "Crystalline"},
    {"고분자명": "ABS", "Abbr": "ABS", "Density": 1.04, "Sol_Param": 9.5, "Structure": "Terpolymer"},
    {"고분자명": "Polytetrafluoroethylene", "Abbr": "PTFE", "Density": 2.20, "Sol_Param": 6.2, "Structure": "Fluorinated"},
    {"고분자명": "Polyoxymethylene (Acetal)", "Abbr": "POM", "Density": 1.41, "Sol_Param": 11.1, "Structure": "Strong crystalline"},
    {"고분자명": "Poly(vinyl alcohol)", "Abbr": "PVA", "Density": 1.29, "Sol_Param": 12.6, "Structure": "Water soluble"},
    {"고분자명": "Polyacrylonitrile", "Abbr": "PAN", "Density": 1.18, "Sol_Param": 12.5, "Structure": "Fiber forming"},
    {"고분자명": "Poly(vinylidene fluoride)", "Abbr": "PVDF", "Density": 1.76, "Sol_Param": 11.0, "Structure": "Piezoelectric"},
    {"고분자명": "Polyurethane", "Abbr": "PU", "Density": 1.20, "Sol_Param": 10.0, "Structure": "Elastomeric"}
]

# --- [앱 로직 시작] ---

st.title("🧪 TSEI 고분자-용매 통합 연구 지원 시스템 V2")
st.markdown("사용자님의 엑셀 데이터를 모두 포함하고 있습니다. 파일 업로드 없이 즉시 사용 가능합니다.")

tab_calc, tab_solv, tab_poly = st.tabs(["📊 PPM 계산기", "💧 용매 23종 DB", "🧬 고분자 18종 DB"])

# 사이드바 환경 설정
with st.sidebar:
    st.header("⚙️ 실험 환경")
    temp = st.slider("실험실 온도 (°C)", 0.0, 40.0, 25.0, 0.1)
    # 온도에 따른 몰부피 보정 계산
    molar_volume = 22.4 * (273.15 + temp) / 273.15
    st.write(f"현재 온도 몰부피: **{molar_volume:.3f} L/mol**")
    st.divider()
    st.info("📍 **도구 사양**\n- 실린지: ~10 μL\n- 피펫: 10~100 μL")

# 1. 계산기 탭
with tab_calc:
    st.subheader("용매 선택 및 주입량 계산")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_solv_name = st.selectbox("용매를 선택하세요 (23종)", [d["용매명"] for d in SOLVENT_DB])
        s_data = next(item for item in SOLVENT_DB if item["용매명"] == selected_solv_name)
        
        mw = st.number_input("분자량 (g/mol)", value=s_data["Mw"], format="%.2f")
        density = st.number_input("밀도 (g/cm³)", value=s_data["Density"], format="%.3f")

    with col2:
        air_vol = st.number_input("Air 주입량 (L)", value=12.0)
        target_ppm = st.number_input("목표 농도 (PPM)", value=1000.0)
    
    with col3:
        purity = st.number_input("시약 순도 (%)", value=100.0)
        st.write("**상세 정보**")
        st.caption(f"끓는점: {s_data['BP']} °C | 친수성: {s_data['친수성']}")

    # 주입량 계산 공식
    req_ul = (target_ppm * mw * air_vol) / (molar_volume * density * (purity/100) * 1000)

    st.divider()
    res_l, res_r = st.columns(2)
    
    with res_l:
        st.markdown(f"""
        <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; border-left: 5px solid #ff4b4b;">
            <p style="margin:0;">필요한 <b>{selected_solv_name}</b> 주입량</p>
            <h1 style="color:#ff4b4b; margin-top:0;">{req_ul:.2f} μL</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with res_r:
        if req_ul <= 10:
            st.warning(f"📍 **추천:** 마이크로 실린지 (눈금: {req_ul:.2f})")
        elif req_ul <= 100:
            st.success(f"📍 **추천:** 마이크로 피펫 ({req_ul:.1f} μL × 1회)")
        else:
            num = math.ceil(req_ul / 100)
            st.success(f"📍 **추천:** 피펫 분할 주입 ({req_ul/num:.1f} μL × {num}번)")

# 2. 용매 DB 탭
with tab_solv:
    st.header("용매 23종 물리적 특성 일람")
    st.dataframe(pd.DataFrame(SOLVENT_DB), use_container_width=True)

# 3. 고분자 DB 탭
with tab_poly:
    st.header("고분자 18종 물리적 특성 요약")
    st.table(pd.DataFrame(POLYMER_DB))

# 하단 수식 안내
st.divider()
st.markdown("### 📝 계산 공식")
st.latex(r"V_{liq}(\mu L) = \frac{PPM \times MW(g/mol) \times V_{air}(L)}{V_m(L/mol) \times \rho(g/mL) \times (Purity/100) \times 1000}")
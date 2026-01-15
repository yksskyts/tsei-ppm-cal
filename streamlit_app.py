import streamlit as st
import pandas as pd
import math

# 1. 페이지 설정
st.set_page_config(page_title="정밀 PPM 계산기 Safety Pro+", page_icon="", layout="wide")

# =========================================================
# (A) 기존 PPM 계산용 기본 물질 리스트 (사용자 코드 유지)
# =========================================================
default_list = [
    {"성분명": "물 (Water)", "분자량": 18.015, "밀도": 1.000, "순도": 100.0, "끓는점": "100.0 °C",
     "인화성": "없음", "독성/위험성": "거의 없음", "특이사항": "전기 기구 접촉 주의"},
    {"성분명": "에탄올 (Ethanol)", "분자량": 46.070, "밀도": 0.789, "순도": 95.0, "끓는점": "78.4 °C",
     "인화성": "높음", "독성/위험성": "눈 자극, 장기 노출 시 간 손상", "특이사항": "화기 엄금"},
    {"성분명": "THF (테트라하이드로퓨란)", "분자량": 72.110, "밀도": 0.890, "순도": 99.5, "끓는점": "66.0 °C",
     "인화성": "매우 높음", "독성/위험성": "심한 눈 자극, 발암성 의심", "특이사항": "과산화물 형성(폭발 위험)"},
    {"성분명": "톨루엔 (Toluene)", "분자량": 92.140, "밀도": 0.870, "순도": 99.5, "끓는점": "110.6 °C",
     "인화성": "높음", "독성/위험성": "생식 독성, 신경계 손상, 흡입 주의", "특이사항": "유기용매 중 독성 강함"},
    {"성분명": "n-헥산 (n-Hexane)", "분자량": 86.180, "밀도": 0.660, "순도": 95.0, "끓는점": "69.0 °C",
     "인화성": "매우 높음", "독성/위험성": "말초 신경 장애, 생식 독성", "특이사항": "장기 노출 시 마비 증상"}
]

# =========================================================
# (B) 이미지 1: 용매 물성표 데이터 (사용자 요청에 따른 키 명칭 변경)
# =========================================================
solvent_props_list = [
    {"용매":"1,2-DCB","δd(분산력)":19.6,"δp(극성력)":6.0,"δh(수소결합력)":3.5,"δt(전체용해도매개변수)":20.8,"유전상수(25C)":9.9,"HLP":19.6,"HLB":"5 ~ 7",
     "BP":180.0,"증기압(mmHg,25C)":0.2,"점도(cP,25C)":1.32,"상대극성지수":10.1,"극성분류":"약극성~중극성","표면장력(mN/m,25C)":37.0,"표면장력상대세기":"중간"},
    {"용매":"Acetone","δd(분산력)":15.5,"δp(극성력)":10.4,"δh(수소결합력)":7.0,"δt(전체용해도매개변수)":19.9,"유전상수(25C)":20.7,"HLP":19.7,"HLB":"10 ~ 12",
     "BP":56.0,"증기압(mmHg,25C)":231.0,"점도(cP,25C)":0.31,"상대극성지수":20.7,"극성분류":"고극성","표면장력(mN/m,25C)":23.7,"표면장력상대세기":"낮음"},
    {"용매":"Anisole","δd(분산력)":17.8,"δp(극성력)":5.7,"δh(수소결합력)":5.9,"δt(전체용해도매개변수)":19.6,"유전상수(25C)":4.3,"HLP":19.1,"HLB":"5 ~ 7",
     "BP":154.0,"증기압(mmHg,25C)":0.4,"점도(cP,25C)":1.07,"상대극성지수":4.3,"극성분류":"약극성","표면장력(mN/m,25C)":34.3,"표면장력상대세기":"중간"},
    {"용매":"Benzyl acetate","δd(분산력)":18.4,"δp(극성력)":5.3,"δh(수소결합력)":6.6,"δt(전체용해도매개변수)":20.3,"유전상수(25C)":5.0,"HLP":19.4,"HLB":"6 ~ 8",
     "BP":206.0,"증기압(mmHg,25C)":0.3,"점도(cP,25C)":1.80,"상대극성지수":"~6.0","극성분류":"약극성","표면장력(mN/m,25C)":36.0,"표면장력상대세기":"중간"},
    {"용매":"Benzyl alcohol","δd(분산력)":18.4,"δp(극성력)":6.3,"δh(수소결합력)":13.7,"δt(전체용해도매개변수)":23.8,"유전상수(25C)":13.1,"HLP":22.3,"HLB":"9 ~ 11",
     "BP":205.0,"증기압(mmHg,25C)":0.1,"점도(cP,25C)":5.47,"상대극성지수":13.1,"극성분류":"고극성","표면장력(mN/m,25C)":39.0,"표면장력상대세기":"강함"},
    {"용매":"Chlorobenzene","δd(분산력)":19.0,"δp(극성력)":4.3,"δh(수소결합력)":2.0,"δt(전체용해도매개변수)":19.6,"유전상수(25C)":5.6,"HLP":19.2,"HLB":"5 ~ 7",
     "BP":132.0,"증기압(mmHg,25C)":11.8,"점도(cP,25C)":0.80,"상대극성지수":5.6,"극성분류":"약극성","표면장력(mN/m,25C)":33.6,"표면장력상대세기":"중간"},
    {"용매":"Chloroform","δd(분산력)":17.8,"δp(극성력)":3.1,"δh(수소결합력)":5.7,"δt(전체용해도매개변수)":18.9,"유전상수(25C)":4.8,"HLP":17.8,"HLB":"2 ~ 4",
     "BP":61.0,"증기압(mmHg,25C)":197.0,"점도(cP,25C)":0.54,"상대극성지수":4.8,"극성분류":"중간극성","표면장력(mN/m,25C)":27.1,"표면장력상대세기":"낮음"},
    {"용매":"Cyclohexane","δd(분산력)":18.0,"δp(극성력)":0.0,"δh(수소결합력)":0.0,"δt(전체용해도매개변수)":18.0,"유전상수(25C)":2.0,"HLP":16.8,"HLB":"1 ~ 3",
     "BP":81.0,"증기압(mmHg,25C)":97.0,"점도(cP,25C)":0.89,"상대극성지수":2.0,"극성분류":"비극성","표면장력(mN/m,25C)":25.5,"표면장력상대세기":"낮음"},
    {"용매":"DCM","δd(분산력)":17.0,"δp(극성력)":7.3,"δh(수소결합력)":7.1,"δt(전체용해도매개변수)":19.8,"유전상수(25C)":8.9,"HLP":20.2,"HLB":"6 ~ 8",
     "BP":40.0,"증기압(mmHg,25C)":435.0,"점도(cP,25C)":0.41,"상대극성지수":9.1,"극성분류":"중간극성","표면장력(mN/m,25C)":27.2,"표면장력상대세기":"낮음"},
    {"용매":"DMF","δd(분산력)":18.0,"δp(극성력)":8.8,"δh(수소결합력)":7.1,"δt(전체용해도매개변수)":21.3,"유전상수(25C)":36.7,"HLP":24.9,"HLB":"12 ~ 14",
     "BP":153.0,"증기압(mmHg,25C)":3.8,"점도(cP,25C)":0.80,"상대극성지수":36.7,"극성분류":"고극성","표면장력(mN/m,25C)":36.4,"표면장력상대세기":"중간"},
    {"용매":"DMSO","δd(분산력)":18.5,"δp(극성력)":14.5,"δh(수소결합력)":19.0,"δt(전체용해도매개변수)":30.2,"유전상수(25C)":46.7,"HLP":26.7,"HLB":"14 ~ 16",
     "BP":189.0,"증기압(mmHg,25C)":0.6,"점도(cP,25C)":1.99,"상대극성지수":46.7,"극성분류":"초극성","표면장력(mN/m,25C)":43.5,"표면장력상대세기":"강함"},
    {"용매":"Ethyl acetate","δd(분산력)":18.2,"δp(극성력)":5.3,"δh(수소결합력)":7.2,"δt(전체용해도매개변수)":20.3,"유전상수(25C)":6.0,"HLP":18.2,"HLB":"7 ~ 9",
     "BP":77.1,"증기압(mmHg,25C)":73.0,"점도(cP,25C)":0.45,"상대극성지수":24.6,"극성분류":"고극성","표면장력(mN/m,25C)":23.9,"표면장력상대세기":"낮음"},
    {"용매":"Ethanol","δd(분산력)":15.6,"δp(극성력)":16.0,"δh(수소결합력)":19.0,"δt(전체용해도매개변수)":29.3,"유전상수(25C)":24.3,"HLP":26.0,"HLB":"14 ~ 16",
     "BP":78.0,"증기압(mmHg,25C)":44.0,"점도(cP,25C)":1.07,"상대극성지수":6.0,"극성분류":"중간극성","표면장력(mN/m,25C)":22.3,"표면장력상대세기":"낮음"},
    {"용매":"Formamide","δd(분산력)":17.1,"δp(극성력)":19.0,"δh(수소결합력)":26.1,"δt(전체용해도매개변수)":36.5,"유전상수(25C)":109.0,"HLP":36.6,"HLB":"18 ~ 20",
     "BP":210.0,"증기압(mmHg,25C)":0.1,"점도(cP,25C)":3.30,"상대극성지수":109.0,"극성분류":"초극성","표면장력(mN/m,25C)":58.2,"표면장력상대세기":"강함"},
    {"용매":"GBL","δd(분산력)":19.0,"δp(극성력)":16.6,"δh(수소결합력)":7.4,"δt(전체용해도매개변수)":26.3,"유전상수(25C)":39.0,"HLP":22.8,"HLB":"12 ~ 14",
     "BP":204.0,"증기압(mmHg,25C)":1.5,"점도(cP,25C)":2.00,"상대극성지수":39.0,"극성분류":"고극성","표면장력(mN/m,25C)":43.8,"표면장력상대세기":"강함"},
    {"용매":"IPA","δd(분산력)":15.8,"δp(극성력)":6.1,"δh(수소결합력)":16.4,"δt(전체용해도매개변수)":23.6,"유전상수(25C)":18.3,"HLP":23.5,"HLB":"12 ~ 14",
     "BP":82.0,"증기압(mmHg,25C)":44.0,"점도(cP,25C)":2.10,"상대극성지수":18.3,"극성분류":"고극성","표면장력(mN/m,25C)":21.7,"표면장력상대세기":"낮음"},
    {"용매":"MEK","δd(분산력)":15.3,"δp(극성력)":9.0,"δh(수소결합력)":4.8,"δt(전체용해도매개변수)":18.4,"유전상수(25C)":18.5,"HLP":19.3,"HLB":"8 ~ 10",
     "BP":79.6,"증기압(mmHg,25C)":88.0,"점도(cP,25C)":0.43,"상대극성지수":7.5,"극성분류":"중간극성","표면장력(mN/m,25C)":24.6,"표면장력상대세기":"낮음"},
    {"용매":"Methanol","δd(분산력)":14.6,"δp(극성력)":9.2,"δh(수소결합력)":16.0,"δt(전체용해도매개변수)":23.5,"유전상수(25C)":32.6,"HLP":29.6,"HLB":"16 ~ 18",
     "BP":64.0,"증기압(mmHg,25C)":96.0,"점도(cP,25C)":0.54,"상대극성지수":32.6,"극성분류":"고극성","표면장력(mN/m,25C)":22.6,"표면장력상대세기":"낮음"},
    {"용매":"NMP","δd(분산력)":18.0,"δp(극성력)":12.3,"δh(수소결합력)":7.2,"δt(전체용해도매개변수)":23.0,"유전상수(25C)":32.2,"HLP":22.9,"HLB":"11 ~ 13",
     "BP":202.0,"증기압(mmHg,25C)":0.3,"점도(cP,25C)":1.65,"상대극성지수":32.0,"극성분류":"고극성","표면장력(mN/m,25C)":40.7,"표면장력상대세기":"강함"},
    {"용매":"THF","δd(분산력)":16.8,"δp(극성력)":5.7,"δh(수소결합력)":8.0,"δt(전체용해도매개변수)":19.5,"유전상수(25C)":7.6,"HLP":19.4,"HLB":"7 ~ 9",
     "BP":66.0,"증기압(mmHg,25C)":143.0,"점도(cP,25C)":0.46,"상대극성지수":7.6,"극성분류":"중간극성","표면장력(mN/m,25C)":26.4,"표면장력상대세기":"낮음"},
    {"용매":"Toluene","δd(분산력)":18.0,"δp(극성력)":1.4,"δh(수소결합력)":2.0,"δt(전체용해도매개변수)":18.2,"유전상수(25C)":2.4,"HLP":18.0,"HLB":"3 ~ 5",
     "BP":111.0,"증기압(mmHg,25C)":28.4,"점도(cP,25C)":0.59,"상대극성지수":2.4,"극성분류":"비극성","표면장력(mN/m,25C)":28.4,"표면장력상대세기":"낮음"},
    {"용매":"Water","δd(분산력)":15.5,"δp(극성력)":16.0,"δh(수소결합력)":42.3,"δt(전체용해도매개변수)":47.8,"유전상수(25C)":78.5,"HLP":23.5,"HLB":"18 ~ 20",
     "BP":100.0,"증기압(mmHg,25C)":23.8,"점도(cP,25C)":0.89,"상대극성지수":78.5,"극성분류":"초극성","표면장력(mN/m,25C)":72.8,"표면장력상대세기":"강함"},
    {"용매":"Xylene","δd(분산력)":18.0,"δp(극성력)":2.5,"δh(수소결합력)":0.0,"δt(전체용해도매개변수)":18.2,"유전상수(25C)":2.3,"HLP":17.8,"HLB":"2 ~ 4",
     "BP":144.0,"증기압(mmHg,25C)":6.6,"점도(cP,25C)":0.76,"상대극성지수":2.5,"극성분류":"비극성","표면장력(mN/m,25C)":28.4,"표면장력상대세기":"낮음"},
]

# =========================================================
# (C) 이미지 2: 고분자 18종 데이터
# =========================================================
polymer_list = [
    {"고분자":"EPDM","극성여부":"비극성","수소결합":"없음","추천용매":"Toluene, Xylene, Cyclohexane",
     "주요특성":"내후성, 내열성, 내화학성 우수"},
    {"고분자":"Poly(4-vinylphenol-co-methyl methacrylate)","극성여부":"극성","수소결합":"있음 (OH기)",
     "추천용매":"DMF, DMSO, NMP, THF, IPA","주요특성":"친수성, 수소결합으로 우수한 접착력과 필름 형성 능력"},
    {"고분자":"Poly(ethylene-co-acrylic acid) (PEAA)","극성여부":"극성","수소결합":"있음 (COOH기)",
     "추천용매":"IPA, Ethanol, DMF, THF","주요특성":"높은 접착성, 친수성, 우수한 유연성과 내충격성"},
    {"고분자":"Poly(styrene-co-maleic acid)","극성여부":"극성","수소결합":"있음 (COOH기)",
     "추천용매":"DMF, DMSO, THF, Acetone","주요특성":"내열성, 투명성 우수, 반응성 높아 표면 개질에 사용"},
    {"고분자":"PVP (Poly(N-vinyl pyrrolidone))","극성여부":"극성","수소결합":"있음 (아마이드기)",
     "추천용매":"Water, Ethanol, IPA, DMF","주요특성":"친수성, 생체적합성 우수, 뛰어난 필름 형성 능력과 안정성"},
    {"고분자":"Poly(2-vinyl pyridine)","극성여부":"중간~강한 극성","수소결합":"약함",
     "추천용매":"DMF, NMP, EtOH, MeOH, DMSO","주요특성":"센서, 전해질, 기능성 고분자 코팅"},
    {"고분자":"Poly(4-vinyl pyridine)","극성여부":"강한 극성","수소결합":"강함",
     "추천용매":"DMF, NMP, MeOH, DMSO","주요특성":"센서, 박막 소자, 습도 감응소자"},
    {"고분자":"Poly(vinyl alcohol-co-vinyl butyral) (PVB)","극성여부":"극성","수소결합":"있음 (OH기)",
     "추천용매":"Ethanol, IPA, THF","주요특성":"투명도, 우수한 접착성 및 필름 형성력, 내충격성 우수"},
    {"고분자":"Cyanoethyl hydroxyethyl cellulose","극성여부":"극성","수소결합":"있음 (OH, CN기)",
     "추천용매":"Water, DMF, DMSO, Formamide","주요특성":"친수성, 우수한 접착력과 필름 형성 능력"},
    {"고분자":"Ethyl cellulose","극성여부":"약극성~비극성","수소결합":"약함 (에테르기)",
     "추천용매":"Ethanol, Acetone, THF","주요특성":"우수한 내수성, 유연한 필름 형성, 비수용성 셀룰로오스 유도체"},
    {"고분자":"Poly(vinyl benzyl chloride)","극성여부":"약극성~비극성","수소결합":"약함",
     "추천용매":"THF, Chloroform, DCM","주요특성":"투명도, 유연성 및 우수한 내화학성"},
    {"고분자":"Poly(ethylene-co-vinyl acetate)","극성여부":"약극성","수소결합":"약함",
     "추천용매":"Toluene, Xylene, Ethyl Acetate, THF","주요특성":"박막 코팅, 방습 포장재, 가스 감응성 재료"},
    {"고분자":"Poly(epichlorohydrin) (PECH)","극성여부":"약극성","수소결합":"약함 (할로겐기)",
     "추천용매":"THF, Chloroform, Toluene","주요특성":"내화학성, 저온에서 탄성 및 접착성 우수"},
    {"고분자":"Poly(epichlorohydrin-co-ethylene oxide)","극성여부":"약극성","수소결합":"약함 (에테르기)",
     "추천용매":"THF, DCM, Chloroform","주요특성":"탄성체 특성, 저온 유연성 및 가공성 우수"},
    {"고분자":"Polystyrene (PS)","극성여부":"비극성","수소결합":"없음",
     "추천용매":"Toluene, Xylene, THF, Chloroform","주요특성":"우수한 전기적 특성, 투명성, 강성 및 내수성 우수"},
    {"고분자":"Polyethylene Oxide (PEO)","극성여부":"극성","수소결합":"있음 (에테르기)",
     "추천용매":"Water, Methanol, Acetonitrile","주요특성":"친수성, 우수한 이온전도성 및 생체적합성"},
    {"고분자":"PMMA","극성여부":"약극성~비극성","수소결합":"약함 (에스터기)",
     "추천용매":"Acetone, THF, Chloroform","주요특성":"높은 투명성, 우수한 기계적 강도, 내후성 및 내화학성 우수"},
    {"고분자":"Poly(Styrene-Maleic Anhydride ester)","극성여부":"약극성~비극성","수소결합":"약함 (에스터기)",
     "추천용매":"THF, DMF, DMSO, Chloroform","주요특성":"필름 형성력 우수, 접착성, 내화학성 및 내열성 뛰어남"},
]

# =========================================================
# (D) 이미지 3: 친수성/혼화성/극성도 요약표 데이터
# =========================================================
solvent_water_list = [
    {"용매명":"Formamide","친수성 등급":"매우 친수성","물과의 혼화성":"완전 혼화","극성도(상대적)":"매우 높음","비고":"극히 친수성, 수소결합 수용 & 제공 가능"},
    {"용매명":"DMSO","친수성 등급":"매우 친수성","물과의 혼화성":"완전 혼화","극성도(상대적)":"매우 높음","비고":"극성 높고 물과 잘 섞임"},
    {"용매명":"DMF","친수성 등급":"매우 친수성","물과의 혼화성":"완전 혼화","극성도(상대적)":"매우 높음","비고":"친수성 강함"},
    {"용매명":"Methanol","친수성 등급":"매우 친수성","물과의 혼화성":"완전 혼화","극성도(상대적)":"매우 높음","비고":"친수성 알코올 계열"},
    {"용매명":"Ethyl Alcohol","친수성 등급":"매우 친수성","물과의 혼화성":"완전 혼화","극성도(상대적)":"매우 높음","비고":"에탄올, 친수성 강함"},
    {"용매명":"IPA","친수성 등급":"매우 친수성","물과의 혼화성":"완전 혼화","극성도(상대적)":"높음","비고":"물과 잘 섞이며 수소결합도 가능"},
    {"용매명":"Acetone","친수성 등급":"매우 친수성","물과의 혼화성":"완전 혼화","극성도(상대적)":"높음","비고":"케톤류, 물에 잘 섞임"},
    {"용매명":"MEK","친수성 등급":"매우 친수성","물과의 혼화성":"완전 혼화","극성도(상대적)":"높음","비고":"Acetone보다 끓는점 높음"},
    {"용매명":"NMP","친수성 등급":"매우 친수성","물과의 혼화성":"완전 혼화","극성도(상대적)":"매우 높음","비고":"고극성 아마이드 계열"},
    {"용매명":"GBL","친수성 등급":"매우 친수성","물과의 혼화성":"완전 혼화","극성도(상대적)":"높음","비고":"수소결합 수용 가능, 물에 잘 섞임"},
    {"용매명":"THF","친수성 등급":"중간 친수성","물과의 혼화성":"완전 혼화","극성도(상대적)":"중간","비고":"물과 혼화되지만 소수성기도 있음"},
    {"용매명":"Ethyl Acetate","친수성 등급":"중간 친수성","물과의 혼화성":"약간 혼화","극성도(상대적)":"중간","비고":"물과 제한적 혼화, 향이 강함"},
    {"용매명":"Chloroform","친수성 등급":"중간 친수성","물과의 혼화성":"제한적","극성도(상대적)":"낮음","비고":"물과 부분 혼화, 밀도 높음"},
    {"용매명":"DCM","친수성 등급":"중간 친수성","물과의 혼화성":"제한적","극성도(상대적)":"중간","비고":"소수성보다 중간 정도"},
    {"용매명":"Anisole","친수성 등급":"중간 친수성","물과의 혼화성":"미혼화","극성도(상대적)":"낮음","비고":"약간 극성이나 전체적으로 소수성"},
    {"용매명":"Chlorobenzene","친수성 등급":"중간 친수성","물과의 혼화성":"미혼화","극성도(상대적)":"낮음","비고":"극성 낮고 소수성 성향"},
    {"용매명":"Benzyl alcohol","친수성 등급":"중간 친수성","물과의 혼화성":"제한적 혼화","극성도(상대적)":"중간~높음","비고":"알코올이지만 분자량 크고 극성 낮음"},
    {"용매명":"Benzyl acetate","친수성 등급":"소수성","물과의 혼화성":"거의 혼화 안 됨","극성도(상대적)":"낮음","비고":"에스터류, 물과 잘 섞이지 않음"},
    {"용매명":"Xylene","친수성 등급":"소수성","물과의 혼화성":"미혼화","극성도(상대적)":"매우 낮음","비고":"방향족, 완전 소수성"},
    {"용매명":"Toluene","친수성 등급":"소수성","물과의 혼화성":"미혼화","극성도(상대적)":"매우 낮음","비고":"방향족 탄화수소, 매우 소수성"},
    {"용매명":"Cyclohexane","친수성 등급":"소수성","물과의 혼화성":"미혼화","극성도(상대적)":"매우 낮음","비고":"완전 소수성, 극성 거의 없음"},
    {"용매명":"1,2-DCB","친수성 등급":"소수성","물과의 혼화성":"미혼화","극성도(상대적)":"매우 낮음","비고":"방향족 할로겐화물, 물과 거의 섞이지 않음"},
    {"용매명":"Water","친수성 등급":"기준 (100%)","물과의 혼화성":"-","극성도(상대적)":"매우 높음","비고":"친수성 기준물질"},
]

# =========================================================
# 2. 세션 상태 초기화
# =========================================================
if "chem_data" not in st.session_state or st.sidebar.button("PPM 데이터 초기화"):
    st.session_state.chem_data = default_list

if "solvent_props" not in st.session_state or st.sidebar.button("용매 물성 데이터 초기화"):
    st.session_state.solvent_props = solvent_props_list

if "polymer_data" not in st.session_state or st.sidebar.button("고분자 데이터 초기화"):
    st.session_state.polymer_data = polymer_list

if "solvent_water" not in st.session_state or st.sidebar.button("친수성/혼화성 데이터 초기화"):
    st.session_state.solvent_water = solvent_water_list

st.title("정밀 가스 농도 계산기 & 용매/고분자 데이터베이스")

# =========================================================
# 3. 공통: 환경 설정 사이드바
# =========================================================
with st.sidebar:
    st.header("환경 설정")
    temp = st.slider("실험실 온도 (°C)", min_value=0.0, max_value=40.0, value=25.0, step=0.1)
    molar_volume = 22.4 * (273.15 + temp) / 273.15
    st.write(f"현재 온도 몰부피: **{molar_volume:.3f} L/mol**")
    st.divider()
    st.info("**도구 사양**\n- 실린지: 10 μL\n- 피펫: 100 μL")

mode = st.sidebar.radio("메뉴", ["PPM 계산", "용매 정보", "고분자 정보"], index=0)

# =========================================================
# 4. 모드 1) PPM 계산 (기존 기능 유지)
# =========================================================
if mode == "PPM 계산":
    st.subheader("1. 성분 데이터 관리")
    col_edit, col_add = st.columns([2, 1])

    with col_add:
        with st.expander("새 성분 직접 추가"):
            with st.form("add_form", clear_on_submit=True):
                name = st.text_input("성분명")
                mw = st.number_input("분자량", min_value=0.0, format="%.3f")
                dens = st.number_input("밀도", min_value=0.0, format="%.3f")
                pur = st.number_input("순도(%)", min_value=0.0, max_value=100.0, value=100.0)
                bp = st.text_input("끓는점 (예: 80.1 °C)")
                inhwa = st.text_input("인화성")
                tox = st.text_input("독성 및 위험성")
                spec = st.text_input("특이사항")
                if st.form_submit_button("리스트에 추가"):
                    if name:
                        new_item = {"성분명": name, "분자량": mw, "밀도": dens, "순도": pur, "끓는점": bp,
                                    "인화성": inhwa, "독성/위험성": tox, "특이사항": spec}
                        st.session_state.chem_data.append(new_item)
                        st.rerun()

    with col_edit:
        df = pd.DataFrame(st.session_state.chem_data)
        for c in ["끓는점", "인화성", "독성/위험성", "특이사항"]:
            if c not in df.columns:
                df[c] = ""
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        st.session_state.chem_data = edited_df.to_dict("records")

    st.divider()
    st.subheader("2. 주입 조건 및 결과")
    c1, c2, c3 = st.columns(3)

    with c1:
        target_chem = st.selectbox("분석할 성분 선택", edited_df["성분명"].tolist())
    with c2:
        air_vol = st.number_input("공기(Air) 주입량 (L)", value=12.0)
    with c3:
        target_ppm = st.number_input("목표 농도 (PPM)", value=1000.0)

    row = edited_df[edited_df["성분명"] == target_chem].iloc[0]
    req_ul = (target_ppm * row["분자량"] * air_vol) / (molar_volume * row["밀도"] * (row["순도"] / 100) * 1000)

    res_c, tool_c = st.columns(2)

    with res_c:
        st.markdown(f"""
        <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; border-left: 5px solid #ff4b4b;">
            <p style="margin:0;">필요한 <b>{target_chem}</b> 총 주입량</p>
            <h1 style="color:#ff4b4b; margin-top:0;">{req_ul:.2f} μL</h1>
        </div>
        """, unsafe_allow_html=True)

    with tool_c:
        st.markdown("### 추천 도구 및 사용법")

        if req_ul <= 10:
            st.warning("**추천 도구:** 마이크로 실린지 (10μL)")
            st.write(f"실린지 눈금을 **{req_ul:.2f}**에 맞춰 1회 주입하세요.")

        elif req_ul <= 100:
            st.success("**추천 도구:** 마이크로 피펫 (100μL)")
            st.markdown(f"""
            <div style="background-color:#e8f4ea; padding:15px; border-radius:10px; border: 1px solid #28a745;">
                <p style="margin:0; font-weight:bold; color:#1e7e34;">피펫 세팅:</p>
                <h2 style="margin:5px 0; color:#1e7e34;">{req_ul:.1f} μL × 1회</h2>
            </div>
            """, unsafe_allow_html=True)

        else:
            num_injections = math.ceil(req_ul / 100)
            vol_per_time = req_ul / num_injections

            st.success("**추천 도구:** 마이크로 피펫 (100μL) - 분할 주입")
            st.markdown(f"""
            <div style="background-color:#e8f4ea; padding:15px; border-radius:10px; border: 1px solid #28a745;">
                <p style="margin:0; font-weight:bold; color:#1e7e34;">회당 세팅 값:</p>
                <h2 style="margin:5px 0; color:#1e7e34;">{vol_per_time:.1f} μL</h2>
                <p style="margin:0; font-weight:bold; color:#1e7e34;">총 주입 횟수: {num_injections}번</p>
                <p style="margin:5px 0 0 0; font-size:14px;">
                    (피펫 다이얼을 {vol_per_time:.1f}에 맞추고 {num_injections}번 나누어 주입하세요)
                </p>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.subheader("물질 안전 및 물리적 특성")
    safe_c1, safe_c2 = st.columns([1, 1])

    with safe_c1:
        inhwa_val = str(row["인화성"])
        icon = "" if "높음" in inhwa_val else ""
        bg_color = "#fff3cd" if "높음" in inhwa_val else "#d4edda"

        st.markdown(f"""
        <div style="background-color:{bg_color}; padding:15px; border-radius:10px; border:1px solid #ffeeba;">
            <p style="margin:0; font-weight:bold;">물리적 특성 및 안전 정보</p>
            <p style="margin:5px 0;"><b>끓는점:</b> <span style="color:#007bff; font-weight:bold;">{row["끓는점"]}</span></p>
            <p style="margin:5px 0;"><b>인화성:</b> {icon}{inhwa_val}</p>
            <p style="margin:5px 0;"><b>독성 및 위험성:</b> {row["독성/위험성"]}</p>
        </div>
        """, unsafe_allow_html=True)

    with safe_c2:
        st.markdown(f"""
        <div style="background-color:#f8d7da; padding:15px; border-radius:10px; border:1px solid #f5c6cb;">
            <p style="margin:0; font-weight:bold; color:#721c24;">특이사항 (주의사항)</p>
            <p style="margin:5px 0; color:#721c24; font-weight:bold;">{row["특이사항"]}</p>
        </div>
        """, unsafe_allow_html=True)

    st.link_button(f"{target_chem} 상세 MSDS 검색", f"https://pubchem.ncbi.nlm.nih.gov/#query={target_chem}")

# =========================================================
# 5. 모드 2) 용매 정보
# =========================================================
elif mode == "용매 정보":
    st.subheader("용매 데이터베이스")

    solvent_df = pd.DataFrame(st.session_state.solvent_props)
    water_df = pd.DataFrame(st.session_state.solvent_water)

    # 검색/필터
    c1, c2 = st.columns([2, 1])
    with c1:
        q = st.text_input("용매명 검색", value="")
    with c2:
        pol_filter = st.selectbox("극성 분류 필터", ["전체"] + sorted(solvent_df["극성분류"].dropna().unique().tolist()))

    view_df = solvent_df.copy()
    if q.strip():
        view_df = view_df[view_df["용매"].str.contains(q, case=False, na=False)]
    if pol_filter != "전체":
        view_df = view_df[view_df["극성분류"] == pol_filter]

    st.dataframe(view_df, use_container_width=True)

    st.divider()
    st.subheader("용매 상세 보기")
    solvent_names = solvent_df["용매"].tolist()
    sel = st.selectbox("용매 선택", solvent_names)
    srow = solvent_df[solvent_df["용매"] == sel].iloc[0]

    left, right = st.columns([1, 1])
    with left:
        st.markdown("### 물성(요약)")
        st.write({
            "δd(분산력)": srow.get("δd(분산력)"),
            "δp(극성력)": srow.get("δp(극성력)"),
            "δh(수소결합력)": srow.get("δh(수소결합력)"),
            "δt(전체용해도매개변수)": srow.get("δt(전체용해도매개변수)"),
            "유전상수(25C)": srow.get("유전상수(25C)"),
            "BP(°C)": srow.get("BP"),
            "증기압(mmHg,25C)": srow.get("증기압(mmHg,25C)"),
            "점도(cP,25C)": srow.get("점도(cP,25C)"),
            "표면장력(mN/m,25C)": srow.get("표면장력(mN/m,25C)"),
            "극성분류": srow.get("극성분류"),
        })

    with right:
        st.markdown("### 물과의 혼화성/친수성")
        # water_df는 용매명 컬럼명이 '용매명'이라 매핑
        wmatch = water_df[water_df["용매명"].str.lower() == str(sel).lower()]
        if len(wmatch) == 0:
            wmatch = water_df[water_df["용매명"].str.contains(sel, case=False, na=False)]

        if len(wmatch) > 0:
            wrow = wmatch.iloc[0]
            st.write({
                "친수성 등급": wrow.get("친수성 등급"),
                "물과의 혼화성": wrow.get("물과의 혼화성"),
                "극성도(상대적)": wrow.get("극성도(상대적)"),
                "비고": wrow.get("비고"),
            })
        else:
            st.info("해당 용매의 친수성/혼화성 데이터가 별도 표에 없습니다.")

# =========================================================
# 6. 모드 3) 고분자 정보
# =========================================================
else:
    st.subheader("고분자 데이터베이스")
    pdf = pd.DataFrame(st.session_state.polymer_data)

    c1, c2 = st.columns([2, 1])
    with c1:
        q = st.text_input("고분자명 검색", value="")
    with c2:
        pol = st.selectbox("극성 여부 필터", ["전체"] + sorted(pdf["극성여부"].dropna().unique().tolist()))

    view_pdf = pdf.copy()
    if q.strip():
        view_pdf = view_pdf[view_pdf["고분자"].str.contains(q, case=False, na=False)]
    if pol != "전체":
        view_pdf = view_pdf[view_pdf["극성여부"] == pol]

    st.dataframe(view_pdf, use_container_width=True)

    st.divider()
    st.subheader("고분자 상세 보기")
    sel_poly = st.selectbox("고분자 선택", pdf["고분자"].tolist())
    prow = pdf[pdf["고분자"] == sel_poly].iloc[0]

    st.markdown("### 요약")
    st.write({
        "극성 여부": prow.get("극성여부"),
        "수소결합": prow.get("수소결합"),
        "추천 용매": prow.get("추천용매"),
        "주요 특성": prow.get("주요특성"),
    })

    # 추천 용매를 DB(용매물성/혼화성)와 연동해 보여주기
    st.markdown("### 추천 용매 상세(연동)")
    solvent_df = pd.DataFrame(st.session_state.solvent_props)
    water_df = pd.DataFrame(st.session_state.solvent_water)

    rec = str(prow.get("추천용매", ""))
    rec_list = [x.strip() for x in rec.split(",") if x.strip()]

    if rec_list:
        matched = solvent_df[solvent_df["용매"].isin(rec_list)]
        if len(matched) > 0:
            st.dataframe(matched, use_container_width=True)
        else:
            st.info("추천 용매가 용매 물성 DB와 표기 불일치로 매칭되지 않았습니다. (표기 통일 필요)")

        # 물 혼화성 표에서도 같이
        wmatched = water_df[water_df["용매명"].isin(rec_list)]
        if len(wmatched) > 0:
            st.dataframe(wmatched, use_container_width=True)
    else:
        st.info("추천 용매 정보가 없습니다.")
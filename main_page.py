import streamlit as st
import pandas as pd

st.markdown("# 数字化风控报告 🎈")
st.sidebar.markdown("# 主页🎈")


# @st.cache()
@st.cache(suppress_st_warning=True)
def get_data_from_excel(filename):
    file = st.file_uploader("请上传您的 {} 文件: ".format(filename),
                            type=['xlsx'])
    data1 = pd.read_excel(
        io=file,
        engine="openpyxl",
        sheet_name=1,
    )
    data2 = pd.read_excel(
        io=file,
        engine="openpyxl",
        sheet_name=2,
    )
    return data1, data2
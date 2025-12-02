import streamlit as st
st.header("1.الزر الاساسي")
if st.button("اضغط هنا للترحيب"):
  st.write("اهلا بك في عالم البرمجة بلغة بايثون")

st.header("اظهار/اخفاء")
if st.checkbox("عرض التفاصيل"):
  st.info("هذه هي التفاصل المخفية")

st.header("زر ملون (primary) ")
st.button("زر تأكيد مهم", type="primary")

st.header("تصميم خاص")
st.markdown("""
<style>
div.stButton > dutton:first-child {
    background-color:#780606;
    color:white;
    font-size:20px;
    border-radius:10px;
    border:2px solid #000000; }
</style>
""",unsafe_allow_html=True)
st.button("زر بتصميم خاص")

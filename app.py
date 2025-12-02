import streamlit as st
st.header("1.الزر الاساسي")
if st.button("اضغط هنا للترحيب"):
  st.write("اهلا بك في عالم البرمجة بلغة بايثون")

st.header("اظهار/اخفاء")
if st.checkbox("عرض التفاصيل"):
  st.info("هذه هي التفاصل المخفية")

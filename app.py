import streamlit as st
st.header("1.الزر الاساسي")
if st.button("اضغط هنا للترحيب"):
  st.write("اهلا بك في عالم البرمجة بلغة بايثون")

st.header("اظهار/اخفاء")
if st.checkbox("عرض التفاصيل"):
  st.info("هذه هي التفاصل المخفية")

st.header("زر ملون (primary) ")
st.button("زر تأكيد مهم", type="primary")

st.header("قائمة")
page=st.radio("," الرأسية "[ , " : اختر الصفحة ] " حول" " و" الاعدادات" , horizontal=True)
if page == "الرأسية":
  st.write("انت في القائمة الرأسية")

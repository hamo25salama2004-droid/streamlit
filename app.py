import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from streamlit_option_menu import option_menu
import time

# --- إعدادات الصفحة وتنسيق الواجهة ---
st.set_page_config(page_title="نظام الكاشير الذكي", layout="wide", page_icon="🛒")

# --- تنسيق CSS مخصص لجعل الموقع جذاب ويدعم العربية ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif;
    }
    
    .stApp {
        background-color: #0e1117;
    }
    
    /* تنسيق الكروت */
    .metric-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
        text-align: center;
        border: 1px solid #4e4e4e;
        transition: transform 0.3s;
    }
    .metric-card:hover {
        transform: scale(1.05);
        border-color: #ff4b4b;
    }
    
    /* تنسيق العناوين */
    h1, h2, h3 {
        color: #ffffff;
        text-align: right;
    }
    
    /* جعل النصوص من اليمين لليسار وتحسين شكل المداخلات */
    .element-container, .stMarkdown, .stTextInput, .stNumberInput, .stSelectbox {
        direction: rtl;
        text-align: right;
    }
    
    /* تحسين شكل الأرقام في شاشة البيع */
    [data-testid="stMetricValue"] {
        font-size: 3em !important; /* حجم أكبر */
        color: #00FF7F !important; /* لون أخضر فاقع وجذاب (Lime Green) */
        text-shadow: 1px 1px 5px rgba(0, 255, 127, 0.5); /* إضافة ظل بسيط */
    }
    
    /* تحسين شكل الأزرار */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 50px;
        font-weight: bold;
        font-size: 18px;
    }
    
    /* تأثيرات حركية */
    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }
    .animate-text {
        animation: fadeIn 1.5s ease-in;
    }
</style>
""", unsafe_allow_html=True)

# --- الاتصال بجوجل شيت ---
@st.cache_resource
def connect_to_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        # **تعديل للتعامل مع التشغيل المحلي والسحابي**
        # 1. التشغيل السحابي (Streamlit Cloud): يستخدم st.secrets
        # 2. التشغيل المحلي: يستخدم الملف credentials.json
        if st.secrets.get("gspread"):
             creds = ServiceAccountCredentials.from_service_account_info(
                st.secrets["gspread"], scope
            )
        else:
             creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
             
        client = gspread.authorize(creds)
        sheet = client.open("Shop_System") # تأكد أن هذا الاسم مطابق لاسم ملفك
        return sheet
    except Exception as e:
        # عرض الخطأ [Errno 2] هنا إذا كان التشغيل محلي
        st.error(f"⚠️ خطأ في الاتصال بقاعدة البيانات: {e}") 
        return None

# دالة لجلب البيانات (مع التخزين المؤقت لتسريع الأداء)
@st.cache_data(ttl=60)
def get_data(sheet_object, worksheet_name):
    if sheet_object is None:
        return pd.DataFrame() # إرجاع داتا فريم فارغ في حال عدم الاتصال
    worksheet = sheet_object.worksheet(worksheet_name)
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

sheet = connect_to_gsheet()
df_inv = get_data(sheet, "Inventory") # تحميل البيانات مرة واحدة

# --- القائمة الجانبية ---
with st.sidebar:
    selected = option_menu(
        menu_title="القائمة الرئيسية",
        options=["شاشة البيع", "إضافة منتج", "المخزون"],
        icons=["cart-check", "plus-circle", "database"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5px", "background-color": "#262730"},
            "icon": {"color": "orange", "font-size": "25px"}, 
            "nav-link": {"font-size": "18px", "text-align": "right", "margin":"0px", "--hover-color": "#333"},
            "nav-link-selected": {"background-color": "#ff4b4b"},
        }
    )
    st.markdown("---")
    st.caption("🚀 نظام متطور v1.0")

# ==========================
# 1. شاشة البيع (POS)
# ==========================
if selected == "شاشة البيع":
    st.markdown("<h1 class='animate-text'>🛒 نقطة البيع الذكية</h1>", unsafe_allow_html=True)
    
    if sheet and not df_inv.empty:
        # التأكد من أن الأعمدة رقمية
        df_inv['Barcode'] = df_inv['Barcode'].astype(str)
        df_inv['Sale Price'] = pd.to_numeric(df_inv['Sale Price'], errors='coerce')
        df_inv['Quantity'] = pd.to_numeric(df_inv['Quantity'], errors='coerce')

        product_found = None
        
        main_container = st.container(border=True) 
        with main_container:
            col_scan, col_details = st.columns([1, 2])
            
            with col_scan:
                st.info("💡 قم بمسح الباركود أو كتابته واضغط Enter")
                barcode_input = st.text_input("باركود المنتج", key="barcode_scanner", placeholder="Scan here...", help="ضع المؤشر هنا واستخدم قارئ الباركود")

            # منطق البحث عن المنتج
            if barcode_input:
                product_found = df_inv[df_inv['Barcode'] == barcode_input]
                
                if not product_found.empty:
                    product_data = product_found.iloc[0]
                    
                    with col_details:
                        # عرض تفاصيل المنتج بشكل جذاب
                        st.markdown(f"""
                        <div class="metric-card">
                            <h2 style="color: #ff4b4b; margin:0;">{product_data['Name']}</h2>
                            <h4 style="color: #ccc;">النوع: {product_data['Type']}</h4>
                            <hr>
                            <h1 style="color: #00FF7F;">{product_data['Sale Price']:,.2f} EGP</h1>
                            <p>الكمية المتاحة بالمخزن: <b>{product_data['Quantity']}</b> | الحد الأدنى للطلب: <b>{product_data['Reorder Level']}</b></p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.write("---")
                    
                    # منطقة إتمام عملية البيع
                    payment_container = st.container(border=True)
                    with payment_container:
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            qty_to_buy = st.number_input("الكمية المطلوبة", min_value=1, max_value=int(product_data['Quantity']), value=1, step=1)
                        
                        total_price = qty_to_buy * product_data['Sale Price']
                        
                        with c2:
                            # عرض الإجمالي بشكل جذاب باستخدام st.metric
                            st.metric(label="الإجمالي المطلوب دفعه", value=f"{total_price:,.2f} EGP")
                        
                        with c3:
                            st.write("##") # مسافة
                            confirm_btn = st.button("✅ إتمام البيع", type="primary")
                        
                        if confirm_btn:
                            if qty_to_buy <= product_data['Quantity']:
                                with st.spinner("جاري تسجيل العملية..."):
                                    # 1. تحديث الكمية في المخزون
                                    inventory_worksheet = sheet.worksheet("Inventory")
                                    cell = inventory_worksheet.find(barcode_input)
                                    current_qty = int(product_data['Quantity'])
                                    new_qty = current_qty - qty_to_buy
                                    
                                    # تحديث الخلية في العمود 6 (الكمية)
                                    inventory_worksheet.update_cell(cell.row, 6, new_qty) 
                                    
                                    # 2. تسجيل البيع في شيت المبيعات
                                    sales_worksheet = sheet.worksheet("Sales")
                                    
                                    # احتساب الربح: (سعر البيع - سعر التكلفة) * الكمية
                                    revenue = (product_data['Sale Price'] - product_data['Cost Price']) * qty_to_buy
                                    
                                    sales_worksheet.append_row([
                                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        product_data['Name'],
                                        qty_to_buy,
                                        total_price,
                                        revenue # تسجيل الربح
                                    ])
                                    
                                    st.balloons()
                                    st.toast(f"تم بيع {qty_to_buy} من {product_data['Name']} بنجاح!", icon="🎉")
                                    st.cache_data.clear() # مسح الكاش لتحديث المخزون فوراً
                                    time.sleep(1)
                                    st.rerun()
                            else:
                                st.error("الكمية المطلوبة غير متاحة في المخزون!")
                else:
                    st.warning("❌ المنتج غير موجود! تأكد من الباركود أو قم بتسجيله أولاً.")
        elif barcode_input:
             st.warning("الرجاء إدخال باركود صالح.")
    elif sheet:
        st.info("المخزون فارغ حالياً. يرجى إضافة منتجات جديدة.")

# ==========================
# 2. إضافة منتج جديد
# ==========================
elif selected == "إضافة منتج":
    st.markdown("<h1 class='animate-text'>📦 تسجيل منتج جديد</h1>", unsafe_allow_html=True)
    
    # حاوية أنيقة لتسجيل المنتج
    with st.form("add_product_form", clear_on_submit=True):
        st.subheader("البيانات الأساسية")
        c1, c2, c3 = st.columns(3)
        with c1:
            new_barcode = st.text_input("الباركود (Barcode)", help="الرقم التعريفي الفريد للمنتج")
        with c2:
            new_name = st.text_input("اسم المنتج")
        with c3:
            new_type = st.selectbox("النوع / التصنيف", ["عام", "إلكترونيات", "ملابس", "أغذية", "أخرى", "مشروبات", "خدمة"])
        
        st.subheader("بيانات التسعير والكميات")
        p1, p2, p3, p4 = st.columns(4)
        with p1:
            new_sale_price = st.number_input("سعر البيع للعميل", min_value=0.0, step=0.5, format="%.2f")
        with p2:
            new_cost_price = st.number_input("سعر التكلفة (للمتجر)", min_value=0.0, step=0.5, format="%.2f", help="مهم لحساب الأرباح")
        with p3:
            new_qty = st.number_input("الكمية الأولية (في المخزون)", min_value=1, step=1)
        with p4:
            new_reorder_level = st.number_input("الحد الأدنى للطلب (Reorder Level)", min_value=0, step=1, value=5, help="لتنبيهك عندما ينخفض المخزون")

        st.markdown("---")
        submitted = st.form_submit_button("💾 حفظ المنتج وتحديث المخزون", type="primary")
        
        if submitted:
            if new_barcode and new_name and sheet:
                inventory_worksheet = sheet.worksheet("Inventory")
                
                # التحقق من عدم التكرار
                try:
                    existing = inventory_worksheet.find(new_barcode)
                    st.error("⚠️ هذا الباركود مسجل مسبقاً! لا يمكن إضافة منتج بنفس الباركود مرتين.")
                except gspread.exceptions.CellNotFound:
                    # البيانات بالترتيب الجديد: Barcode, Name, Type, Sale Price, Cost Price, Quantity, Reorder Level
                    inventory_worksheet.append_row([
                        new_barcode, 
                        new_name, 
                        new_type, 
                        new_sale_price, 
                        new_cost_price,
                        new_qty,
                        new_reorder_level
                    ])
                    st.success(f"تم إضافة {new_name} للمخزون بنجاح!")
                    st.balloons()
                    st.cache_data.clear() # مسح الكاش لتحديث جدول المخزون
            else:
                st.warning("يرجى ملء حقول الباركود واسم المنتج والأسعار على الأقل.")

# ==========================
# 3. عرض المخزون (للمتابعة)
# ==========================
elif selected == "المخزون":
    st.markdown("<h1 class='animate-text'>📊 حالة المخزون الحالية</h1>", unsafe_allow_html=True)
    
    if sheet:
        # إعادة تحميل البيانات هنا دون الكاش لتكون محدثة تماماً
        df_display = get_data(sheet, "Inventory") 
        
        if not df_display.empty:
            
            # التأكد من تحويل الأعمدة الرقمية
            df_display['Quantity'] = pd.to_numeric(df_display['Quantity'], errors='coerce').fillna(0)
            df_display['Sale Price'] = pd.to_numeric(df_display['Sale Price'], errors='coerce').fillna(0)
            df_display['Reorder Level'] = pd.to_numeric(df_display['Reorder Level'], errors='coerce').fillna(0)

            # دالة تلوين الصفوف ذات المخزون المنخفض
            def color_low_stock(row):
                if row['Quantity'] <= row['Reorder Level']:
                    # اللون الأحمر للخلفية والخط الأصفر للتنبيه
                    return ['background-color: #58151C; color: #FFA500'] * len(row)
                return [''] * len(row)

            st.dataframe(
                df_display.style.apply(color_low_stock, axis=1), 
                use_container_width=True,
                column_config={
                    "Sale Price": st.column_config.NumberColumn("سعر البيع", format="%.2f EGP"),
                    "Cost Price": st.column_config.NumberColumn("سعر التكلفة", format="%.2f EGP"),
                    "Quantity": st.column_config.NumberColumn("الكمية المتاحة"),
                    "Reorder Level": st.column_config.NumberColumn("حد إعادة الطلب"),
                }
            )
            
            st.markdown("### إحصائيات سريعة")
            k1, k2, k3 = st.columns(3)
            k1.metric("عدد الأصناف", len(df_display))
            k2.metric("إجمالي القطع", int(df_display['Quantity'].sum()))
            
            total_value = (df_display['Quantity'] * df_display['Sale Price']).sum()
            k3.metric("القيمة التقديرية للمخزون", f"{total_value:,.2f} EGP")
        else:
            st.info("المخزون فارغ حالياً.")

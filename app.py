import streamlit as st
import time
import pickle
import os

# --- 🛠️ الثوابت والإعدادات الأولية ---

# ملف حفظ البيانات
DATA_FILE = 'quiz_data.pkl'
# اسم المستخدم وكلمة المرور للإعدادات
ADMIN_USERNAME = '2025'
ADMIN_PASSWORD = '2026'
# إجمالي وقت الاختبار بالثواني (يمكن تغييره في الإعدادات لاحقاً)
DEFAULT_QUIZ_TIME = 600  # 10 دقائق

# --- 💾 وظائف حفظ وتحميل البيانات ---

def load_data():
    """تحميل بيانات الأسئلة من الملف."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'rb') as f:
            return pickle.load(f)
    return {'questions': [], 'quiz_time': DEFAULT_QUIZ_TIME}

def save_data(data):
    """حفظ بيانات الأسئلة في الملف."""
    with open(DATA_FILE, 'wb') as f:
        pickle.dump(data, f)

# تهيئة الجلسة وتحميل البيانات عند بدء تشغيل التطبيق
if 'data' not in st.session_state:
    st.session_state.data = load_data()
    st.session_state.logged_in = False
    st.session_state.current_page = 'main'
    st.session_state.quiz_in_progress = False

# --- 🔑 صفحة تسجيل الدخول (الإعدادات) ---

def login_page():
    """واجهة تسجيل الدخول للإعدادات."""
    st.header("🔑 تسجيل الدخول للإعدادات")
    
    with st.form("login_form"):
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        submit_button = st.form_submit_button("تسجيل الدخول")

        if submit_button:
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.current_page = 'settings'
                st.rerun() # لإعادة تحميل الصفحة وعرض الإعدادات
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة.")

# --- ⚙️ صفحة الإعدادات (بعد تسجيل الدخول) ---

def settings_page():
    """واجهة إدارة الأسئلة وتعديل وقت الاختبار."""
    st.header("⚙️ إعدادات الاختبار")
    
    if st.button("العودة للصفحة الرئيسية"):
        st.session_state.current_page = 'main'
        st.rerun()
        return

    # 1. إدارة وقت الاختبار
    st.subheader("⏱️ إعداد وقت الاختبار الكلي")
    new_quiz_time_min = st.number_input(
        "وقت الاختبار (بالدقائق)",
        min_value=1, 
        max_value=120, 
        value=int(st.session_state.data['quiz_time'] / 60)
    )
    if st.button("تحديث وقت الاختبار"):
        st.session_state.data['quiz_time'] = new_quiz_time_min * 60
        save_data(st.session_state.data)
        st.success(f"تم تحديث وقت الاختبار إلى {new_quiz_time_min} دقيقة.")

    st.markdown("---")
    
    # 2. إضافة سؤال جديد
    st.subheader("➕ إضافة سؤال جديد")
    with st.form("add_question_form", clear_on_submit=True):
        q_text = st.text_area("نص السؤال")
        q_option_a = st.text_input("الخيار أ")
        q_option_b = st.text_input("الخيار ب")
        q_option_c = st.text_input("الخيار ج")
        q_option_d = st.text_input("الخيار د")
        
        # قائمة الخيارات المتاحة لتحديد الإجابة الصحيحة
        options_list = ['أ', 'ب', 'ج', 'د']
        correct_answer_label = st.selectbox(
            "الإجابة الصحيحة هي:",
            options_list
        )
        
        q_score = st.number_input("درجة السؤال:", min_value=1, value=5)
        
        add_button = st.form_submit_button("إضافة السؤال")
        
        if add_button:
            if q_text and q_option_a and q_option_b and q_option_c and q_option_d:
                # ربط التسمية (أ، ب، ج، د) بالنص الفعلي للإجابة
                options_map = {
                    'أ': q_option_a, 'ب': q_option_b, 
                    'ج': q_option_c, 'د': q_option_d
                }
                
                new_question = {
                    'text': q_text,
                    'options': [q_option_a, q_option_b, q_option_c, q_option_d],
                    'correct_answer': options_map[correct_answer_label], # حفظ النص الفعلي للإجابة الصحيحة
                    'score': q_score
                }
                st.session_state.data['questions'].append(new_question)
                save_data(st.session_state.data)
                st.success("تم إضافة السؤال بنجاح!")
            else:
                st.error("الرجاء ملء جميع حقول السؤال.")
    
    st.markdown("---")
    
    # 3. عرض ومراجعة الأسئلة
    st.subheader(f"📝 قائمة الأسئلة الحالية ({len(st.session_state.data['questions'])} سؤال)")
    
    for i, q in enumerate(st.session_state.data['questions']):
        st.write(f"**سؤال {i+1} (الدرجة: {q['score']}):** {q['text']}")
        st.write(f"الإجابة الصحيحة: **{q['correct_answer']}**")
        if st.button(f"حذف سؤال {i+1}", key=f"delete_{i}"):
            st.session_state.data['questions'].pop(i)
            save_data(st.session_state.data)
            st.success(f"تم حذف السؤال {i+1}.")
            st.rerun()

# --- 📝 صفحة حل الاختبار ---

def quiz_page():
    """واجهة عرض وحل الاختبار وحساب النتيجة."""
    questions = st.session_state.data['questions']
    total_time = st.session_state.data['quiz_time']
    
    if not questions:
        st.warning("لا يوجد أسئلة حالياً. يرجى إضافة أسئلة من صفحة الإعدادات.")
        if st.button("العودة للصفحة الرئيسية"):
            st.session_state.current_page = 'main'
            st.rerun()
        return

    # بدء الاختبار ومنطق الوقت
    if not st.session_state.quiz_in_progress:
        st.session_state.quiz_in_progress = True
        st.session_state.start_time = time.time()
        # تهيئة إجابات المستخدم
        st.session_state.user_answers = [None] * len(questions)
        st.session_state.show_results = False

    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = max(0, total_time - elapsed_time)
    
    # عرض العداد
    time_placeholder = st.empty()

    if remaining_time > 0 and not st.session_state.show_results:
        # تنسيق الوقت المتبقي
        mins = int(remaining_time // 60)
        secs = int(remaining_time % 60)
        time_placeholder.markdown(f"**⏱️ الوقت المتبقي:** **{mins:02d}:{secs:02d}**")
        
        # تشغيل التحديث الذاتي (ضروري لعرض عداد الوقت في Streamlit)
        if secs % 5 == 0:  # تحديث كل 5 ثواني لتخفيف الحمل
             time.sleep(1)
             st.rerun()

    elif remaining_time <= 0 and not st.session_state.show_results:
        # انتهاء الوقت
        st.warning("🚫 انتهى الوقت! سيتم عرض النتيجة الآن.")
        st.session_state.show_results = True
        # لا حاجة لإعادة التشغيل، سيتم عرض النتيجة مباشرة
    
    st.markdown("---")
    
    if st.session_state.show_results:
        # --- عرض النتيجة بعد انتهاء الاختبار ---
        st.header("🎉 نتيجة الاختبار")
        total_score = 0
        max_score = sum(q['score'] for q in questions)
        
        for i, q in enumerate(questions):
            user_answer = st.session_state.user_answers[i]
            is_correct = user_answer == q['correct_answer']
            
            st.markdown(f"**سؤال {i+1}** ({q['score']} نقطة): {q['text']}")
            
            # تحديد الإجابة التي اختارها المستخدم وتلوينها
            if user_answer is not None:
                if is_correct:
                    st.success(f"إجابتك: {user_answer} (صحيحة!)")
                    total_score += q['score']
                else:
                    st.error(f"إجابتك: {user_answer} (خاطئة)")
                    st.info(f"الإجابة الصحيحة: **{q['correct_answer']}**")
            else:
                st.warning("لم تجب على هذا السؤال.")
                st.info(f"الإجابة الصحيحة: **{q['correct_answer']}**")
                
            st.markdown("---")

        st.success(f"**النتيجة النهائية:** **{total_score}** من **{max_score}**")
        
        if st.button("بدء اختبار جديد"):
            # إعادة تعيين حالة الاختبار
            st.session_state.quiz_in_progress = False
            st.session_state.show_results = False
            st.session_state.current_page = 'main'
            st.rerun()

    else:
        # --- واجهة حل الأسئلة أثناء الاختبار ---
        
        # عرض عدد الأسئلة المجاب عليها (أو تم التوقف عندها)
        answered_count = sum(1 for ans in st.session_state.user_answers if ans is not None)
        st.info(f"عدد الأسئلة المجابة: {answered_count} / {len(questions)}")
        
        for i, q in enumerate(questions):
            # استخدام radio button لعرض الخيارات واختيار الإجابة
            st.subheader(f"سؤال {i+1} (الدرجة: {q['score']})")
            
            # قائمة الخيارات
            options = q['options']
            
            # تحديد القيمة الافتراضية بناءً على الإجابة المخزنة مسبقاً
            default_index = None
            if st.session_state.user_answers[i] in options:
                default_index = options.index(st.session_state.user_answers[i])
            
            # استخدام عنصر فارغ (None) كخيار أول ليتمكن المستخدم من "عدم الإجابة" بشكل واضح
            options_with_none = [None] + options
            
            # تغيير الخيار عند تفاعل المستخدم
            selected_option = st.radio(
                q['text'], 
                options_with_none, 
                index=default_index + 1 if default_index is not None else 0, # إضافة 1 لأننا أضفنا None في البداية
                key=f"q_{i}_radio"
            )
            
            # تحديث إجابة المستخدم في الـ session state
            st.session_state.user_answers[i] = selected_option
            
            st.markdown("***") # فاصل بين الأسئلة
            
        # زر إنهاء الاختبار يدوياً
        if st.button("إنهاء الاختبار وعرض النتيجة"):
            st.session_state.show_results = True
            st.rerun()

        # ملاحظة: Streamlit لا يوقف الكود فعلياً عند انتهاء الوقت،
        # لكن المنطق يقوم بإخفاء واجهة الإجابات وعرض النتيجة عند نفاذ الوقت

# --- 🏠 وظيفة توجيه الصفحات الرئيسية ---

def main_page():
    """الصفحة الرئيسية لاختيار الوضع."""
    st.header("اختبار المبرمجين")
    st.image("", width=200)

    st.markdown("---")
    
    st.subheader("اختر وضع التشغيل:")

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("1️⃣ حل الاختبار", use_container_width=True):
            st.session_state.current_page = 'quiz'
            st.session_state.quiz_in_progress = False # تأكد من إعادة التهيئة
            st.rerun()
            
    with col2:
        if st.button("2️⃣ الإعدادات (للمدير)", use_container_width=True):
            st.session_state.current_page = 'login'
            st.rerun()

# --- 🚀 تشغيل التطبيق ---

def run_app():
    """المنطق الرئيسي لتشغيل التطبيق."""
    st.set_page_config(page_title="نظام الاختبارات", layout="wide")
    
    if st.session_state.current_page == 'main':
        main_page()
    elif st.session_state.current_page == 'login':
        login_page()
    elif st.session_state.current_page == 'settings':
        if st.session_state.logged_in:
            settings_page()
        else:
            st.session_state.current_page = 'login'
            st.rerun()
    elif st.session_state.current_page == 'quiz':
        quiz_page()

if __name__ == "__main__":
    run_app()

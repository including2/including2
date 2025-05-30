import streamlit as st
import gspread
import pandas as pd
import json
from google.oauth2.service_account import Credentials

# ===== الاتصال بـ Google Sheets =====
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"])
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
client = gspread.authorize(creds)

# ===== إعادة توجيه حسب الصلاحيات =====
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("🔐 يجب تسجيل الدخول أولاً")
    st.switch_page("home.py")

if st.session_state.get("permissions") != "admin":
    permission = st.session_state.get("permissions")
    if permission == "user":
        st.switch_page("pages/UserDashboard.py")
    elif permission in ["supervisor", "sp"]:
        st.switch_page("pages/Supervisor.py")
    else:
        st.switch_page("home.py")

# ===== إعدادات الشيت الرئيسي =====
ADMIN_SHEET_ID = "1gOmeFwHnRZGotaUHqVvlbMtVVt1A2L7XeIuolIyJjAY"
spreadsheet = client.open_by_key(ADMIN_SHEET_ID)
admin_sheet = spreadsheet.worksheet("admin")
users_df = pd.DataFrame(admin_sheet.get_all_records())

# ===== إعداد الصفحة =====
st.set_page_config(page_title="لوحة الأدمن", page_icon="🛠️")
st.title("🛠️ لوحة إدارة المستخدمين")

# ===== زر التحديث اليدوي =====
if st.button("🔄 جلب المعلومات من قاعدة البيانات"):
    st.cache_data.clear()
    st.rerun()

# ===== الأعمدة الافتراضية لكل مستخدم جديد =====
def get_default_columns():
    return [
        "التاريخ",
        "صلاة الفجر",
        "صلاة الظهر",
        "صلاة العصر",
        "صلاة المغرب",
        "صلاة العشاء",
        "االسنن الرواتب",
        "اورد الإمام النووي رحمه الله",
        "مختصر إشراق الضياء",
        "سنة الوتر",
        "سنة الضحى",
        "حضور درس",
        "تلاوة قرآن (لا يقل عن ثمن)",
        "الدعاء مخ العبادة",
        "قراءة كتاب شرعي",
        "لا إله إلا الله",
        "الاستغفار",
        "الصلاة على سيدنا رسول الله صلى الله عليه وسلم",
        "تطوع ( خبئية - أوابين - تسابيح )"
    ]

# ===== عرض المشرفين في النظام =====
# قراءة المشرفين فقط
supervisors_df = users_df[users_df["role"] == "supervisor"]

# ===== إنشاء مستخدم جديد =====
st.subheader("➕ إنشاء حساب جديد")
with st.form("create_user_form"):
    username = st.text_input("Username")
    password = st.text_input("Password")
    role = "user"  # تم تثبيت الصلاحية على user فقط

    # اختيار المشرف من قائمة المشرفين فقط
    mentor_options = supervisors_df["username"].tolist()  # أسماء المشرفين فقط
    mentor = st.selectbox("اختار المشرف", mentor_options)  # اختيار المشرف

    create = st.form_submit_button("Create")

    if create:
        if not username or not password or not mentor:
            st.warning("يرجى إدخال اسم المستخدم وكلمة المرور واختيار المشرف")
        elif username in users_df["username"].values:
            st.error("🚫 اسم المستخدم موجود مسبقًا")
        else:
            try:
                worksheet_name = f"بيانات - {username}"
                worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows="1000", cols="30")
                worksheet.insert_row(get_default_columns(), 1)
                admin_sheet.append_row([username, password, worksheet_name, role, mentor])  # إضافة المشرف
                st.success("✅ تم إنشاء المستخدم والورقة بنجاح")
                st.rerun()
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء إنشاء المستخدم: {e}")

# ===== عرض المستخدمين =====
st.subheader("📋 قائمة المستخدمين")

# عرض جميع المستخدمين مع الأعمدة المطلوبة فقط
filtered_df = users_df[["username", "role", "Mentor"]]  # اختيار الأعمدة المطلوبة
st.dataframe(filtered_df, use_container_width=True)

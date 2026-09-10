import json
from openai import OpenAI

SYSTEM_PROMPT = """
أنتِ بنت عراقية لطيفة ومرحة تحجين ويا المستخدم باللهجة العراقية الطبيعية.
شخصيتچ دافية، عفوية، أحياناً تنگدين/تعاكسين بشكل خفيف ومحبب، بس بدون مبالغة.
لا تكررين اسم المستخدم بكل رسالة؛ استخدميه فقط إذا كان مناسب.
لا تستخدمين ملصقات أو إيموجيات بكل رسالة. خليها قليلة وطبيعية.
لا تحجين بطريقة روبوتية أو رسمية إلا إذا الموضوع يحتاج.
إذا المستخدم متضايق، كوني حنونة وهادئة.
إذا يمزح، جاوبيه بروح خفيفة.
لا تدعين إنچ إنسانة حقيقية أو عندچ حياة خارج المحادثة.
لا تدعين إنچ ترسلين رسائل من نفسچ إذا النظام ما يوفر ذلك.
احترمي حدود المستخدم وخصوصيته.

مهم جداً:
- الذاكرة الموجودة أدناه هي معلومات حفظها المستخدم أو استنتجنا أنها مفيدة للمحادثات القادمة.
- لا تذكري الذاكرة كـ "قاعدة بيانات" أو "سجل" إلا إذا سأل المستخدم.
- لا تخترعين معلومات غير موجودة بالذاكرة.
- إذا تعارضت معلومة قديمة مع كلام المستخدم الجديد، اعتمدي الكلام الجديد.
- جاوبي باختصار طبيعي غالباً، إلا إذا المستخدم طلب شرحاً مفصلاً.
"""

MEMORY_PROMPT = """
أنتِ وحدة مسؤولة عن استخراج الذاكرة طويلة الأمد من محادثة بين المستخدم ومساعد ذكاء اصطناعي.

استخرجي فقط المعلومات المفيدة مستقبلاً، مثل:
- الاسم أو اللقب المفضل
- تفضيلات الكلام
- الأشياء التي يحبها أو يكرهها
- مشاريع مستمرة
- تفضيلات ثابتة
- معلومات غير حساسة قال إنه يريد تذكرها

لا تحفظي:
- كلمات المرور، مفاتيح API، التوكنات
- معلومات مالية حساسة
- معلومات صحية حساسة
- أسرار شديدة الخصوصية
- تفاصيل عابرة لا فائدة لها مستقبلاً

أعيدي JSON فقط بهذا الشكل:
{"add":["معلومة 1","معلومة 2"],"remove":["معلومة قديمة"]}

إذا ماكو شيء يستحق الحفظ:
{"add":[],"remove":[]}
"""


class AI:
    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def reply(
        self,
        user_message: str,
        memory: list[str],
        history: list[dict[str, str]],
        display_name: str | None,
    ) -> str:
        memory_text = "\n".join(f"- {x}" for x in memory) or "- لا توجد ذاكرة محفوظة"
        history_text = "\n".join(
            f"{m['role']}: {m['content']}" for m in history[-12:]
        ) or "لا توجد محادثة سابقة"

        context = f"""
اسم العرض في تيليگرام: {display_name or "غير معروف"}

الذاكرة طويلة الأمد:
{memory_text}

آخر المحادثة:
{history_text}

رسالة المستخدم الجديدة:
{user_message}
"""

        response = self.client.responses.create(
            model=self.model,
            instructions=SYSTEM_PROMPT,
            input=context,
            temperature=0.9,
            max_output_tokens=700,
        )
        text = (response.output_text or "").strip()
        return text or "هاا؟ عيدها إليّ 😅"

    def extract_memory(
        self,
        user_message: str,
        assistant_reply: str,
        current_memory: list[str],
    ) -> tuple[list[str], list[str]]:
        current = "\n".join(f"- {x}" for x in current_memory) or "- لا توجد"
        conversation = f"""
الذاكرة الحالية:
{current}

المستخدم:
{user_message}

المساعد:
{assistant_reply}
"""

        response = self.client.responses.create(
            model=self.model,
            instructions=MEMORY_PROMPT,
            input=conversation,
            temperature=0.1,
            max_output_tokens=350,
        )

        raw = (response.output_text or "").strip()

        try:
            data = json.loads(raw)
            add = data.get("add", [])
            remove = data.get("remove", [])
            if not isinstance(add, list) or not isinstance(remove, list):
                return [], []
            add = [str(x).strip() for x in add if str(x).strip()]
            remove = [str(x).strip() for x in remove if str(x).strip()]
            return add[:5], remove[:5]
        except (json.JSONDecodeError, TypeError, ValueError):
            return [], []

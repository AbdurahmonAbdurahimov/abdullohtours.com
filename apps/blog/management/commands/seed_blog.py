"""
Phase 3 seed data (CLAUDE.md §13): real, original blog posts.

Idempotent — safe to re-run. Content is original writing for this seed pass,
not scraped or paraphrased from another site (CLAUDE.md §7). English is the
launch language per CLAUDE.md §12; Russian is added because §12 lists RU as
getting "full content including blog" at launch.
"""

from __future__ import annotations

from datetime import UTC, datetime

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.blog.models import BlogPost
from apps.catalog.models import Destination, Package


class Command(BaseCommand):
    help = "Seed Phase 3 blog posts (EN + RU)."

    def handle(self, *args, **options):
        destinations = {d.slug: d for d in Destination.objects.all()}
        packages = {p.slug: p for p in Package.objects.all()}

        for row in POSTS:
            related_dest_slugs = row.pop("related_destinations", [])
            related_pkg_slugs = row.pop("related_packages", [])
            slug = slugify(row["title"])
            post, _ = BlogPost.objects.update_or_create(
                slug=slug,
                defaults={
                    **row,
                    "status": BlogPost.Status.PUBLISHED,
                    "translation_complete_ru": True,
                },
            )
            post.related_destinations.set(
                [destinations[s] for s in related_dest_slugs if s in destinations]
            )
            post.related_packages.set([packages[s] for s in related_pkg_slugs if s in packages])

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(POSTS)} blog posts."))


POSTS = [
    {
        "title": "How Much Does a Private Tour of Uzbekistan Cost?",
        "title_ru": "Сколько стоит частный тур по Узбекистану?",
        "excerpt": (
            "A straight answer on private tour pricing in Uzbekistan — what's "
            "included, what counts as an extra, and why the price is per "
            "vehicle, not per person."
        ),
        "excerpt_ru": (
            "Прямой ответ о ценах на частные туры по Узбекистану — что входит "
            "в стоимость, что оплачивается отдельно и почему цена указывается "
            "за автомобиль, а не за человека."
        ),
        "author": "Abdulloh Tours",
        "category": "Planning",
        "published_at": datetime(2026, 3, 3, 9, 0, tzinfo=UTC),
        "meta_title": "Uzbekistan Private Tour Cost: A Realistic Breakdown",
        "meta_description": (
            "What a private Uzbekistan tour actually costs — transport, guide, "
            "entrance tickets and hotels, broken down per vehicle rather than "
            "per person."
        ),
        "body": (
            "<p>The most common question we get before a trip isn't \"what's included\" "
            "— it's \"how much will this actually cost.\" It's a fair question, and it "
            'deserves a straight answer rather than a vague "contact us for pricing." '
            "So here's how it actually breaks down.</p>"
            "<h2>Pricing is per vehicle, not per person</h2>"
            "<p>This is the single most important thing to understand about how we "
            "price a trip: the vehicle and driver are quoted as a flat daily rate, "
            "split however many people are travelling together. A sedan for two "
            "people and a sedan for three people cost the same to run — so the price "
            "is the same. Group travel gets cheaper per person automatically, without "
            "us needing to build separate group discounts.</p>"
            "<h2>What's included in the vehicle rate</h2>"
            "<ul>"
            "<li>The vehicle itself, sized to your group (sedan, minivan or minibus)</li>"
            "<li>An English-speaking driver</li>"
            "<li>Fuel and standard road costs between cities</li>"
            "</ul>"
            "<h2>What counts as an extra</h2>"
            "<p>A few things are priced separately because they scale with the number "
            "of people, not the vehicle: entrance tickets to sites like the Registan "
            "or Itchan Kala, a professional guide if you want one (we default to "
            "driver-only, guide is optional), and hotels if you'd like us to book "
            "them rather than arranging your own.</p>"
            "<h2>A rough range, so you have a number to start from</h2>"
            "<p>As a loose starting point: a 5-day Tashkent–Samarkand–Bukhara route in "
            "a sedan runs somewhere in the low hundreds of dollars per day for "
            "transport, before entrance tickets. An 8–10 day trip that also covers "
            "Khiva, with a guide and hotels included, costs more in total but usually "
            "less per person once you're travelling as a group of three or four.</p>"
            "<h2>How to get an exact number</h2>"
            "<p>Because pricing depends on your dates, group size and which sites you "
            "want to include, we don't publish a fixed price list — we build a real "
            "quote from your actual plan. The fastest way is our "
            '<a href="/en/build/">tour builder</a>, which gives you a live estimate as '
            "you choose dates, destinations and add-ons. Nothing is charged online: "
            "once you submit, we confirm the final number with you directly on "
            "WhatsApp.</p>"
        ),
        "body_ru": (
            '<p>Самый частый вопрос, который нам задают перед поездкой — не "что '
            'входит в тур", а "сколько это будет стоить на самом деле". Вопрос '
            "справедливый, и он заслуживает прямого ответа, а не расплывчатого "
            '"свяжитесь с нами для расчёта цены". Разберём по пунктам.</p>'
            "<h2>Цена — за автомобиль, а не за человека</h2>"
            "<p>Это главное, что нужно понимать о нашем ценообразовании: автомобиль с "
            "водителем оценивается фиксированной ставкой в сутки, которая делится на "
            "всех участников поездки. Седан для двух человек и седан для трёх стоит "
            "эксплуатировать одинаково — значит, и цена одинакова. При групповой "
            "поездке цена на человека автоматически снижается, без специальных "
            "групповых скидок.</p>"
            "<h2>Что входит в стоимость автомобиля</h2>"
            "<ul>"
            "<li>Сам автомобиль, подобранный по размеру вашей группы (седан, минивэн "
            "или микроавтобус)</li>"
            "<li>Англоговорящий водитель</li>"
            "<li>Топливо и стандартные дорожные расходы между городами</li>"
            "</ul>"
            "<h2>Что оплачивается отдельно</h2>"
            "<p>Отдельно оплачивается то, что зависит от числа людей, а не от "
            "автомобиля: входные билеты на такие объекты, как Регистан или "
            "Ичан-Кала, услуги гида, если он нужен (по умолчанию — только водитель, "
            "гид добавляется по желанию), и отели, если вы хотите, чтобы их "
            "забронировали мы, а не самостоятельно.</p>"
            "<h2>Примерный ориентир по цене</h2>"
            "<p>Как грубый ориентир: 5-дневный маршрут Ташкент–Самарканд–Бухара на "
            "седане обходится в пределах пары сотен долларов в день за транспорт, "
            "без учёта входных билетов. Поездка на 8–10 дней с посещением Хивы, "
            "гидом и отелями стоит больше в сумме, но обычно дешевле на человека при "
            "поездке группой из трёх-четырёх человек.</p>"
            "<h2>Как получить точную цифру</h2>"
            "<p>Поскольку цена зависит от дат, размера группы и выбранных объектов, "
            "мы не публикуем фиксированный прайс-лист — мы считаем реальную смету по "
            "вашему конкретному плану. Быстрее всего это сделать через наш "
            '<a href="/ru/build/">конструктор тура</a>, который показывает примерную '
            "стоимость сразу при выборе дат, направлений и услуг. Онлайн-оплаты нет: "
            "после отправки заявки мы согласуем точную цифру с вами напрямую в "
            "WhatsApp.</p>"
        ),
        "related_packages": [
            "silk-road-highlights",
            "classic-uzbekistan",
            "grand-uzbekistan-mountains",
        ],
    },
    {
        "title": "Best Time to Visit Uzbekistan: A Month-by-Month Guide",
        "title_ru": "Лучшее время для поездки в Узбекистан: гид по месяцам",
        "excerpt": (
            "Uzbekistan has a real continental climate — brutal summer heat, cold "
            "winters, and two short, excellent shoulder seasons. Here's how to plan "
            "around it."
        ),
        "excerpt_ru": (
            "В Узбекистане настоящий континентальный климат — жаркое лето, холодная "
            "зима и два коротких, но отличных межсезонья. Разбираем, как под это "
            "спланировать поездку."
        ),
        "author": "Abdulloh Tours",
        "category": "Planning",
        "published_at": datetime(2026, 3, 10, 9, 0, tzinfo=UTC),
        "meta_title": "Best Time to Visit Uzbekistan (Month by Month)",
        "meta_description": (
            "When to visit Uzbekistan: why April–June and September–November "
            "beat the summer heat and winter cold for Samarkand, Bukhara and "
            "Khiva."
        ),
        "body": (
            "<p>Uzbekistan sits deep inland, with no coastline to soften the "
            "temperature swings — which means the difference between visiting in "
            "May and visiting in July is much bigger than most first-time visitors "
            "expect.</p>"
            "<h2>Spring (April–early June): the best all-round window</h2>"
            "<p>This is the season we recommend most often. Daytime temperatures "
            "sit in a comfortable range for walking around the Registan or Itchan "
            "Kala for hours, the countryside is green, and it's before the peak "
            "summer crowds.</p>"
            "<h2>Summer (mid-June–August): hot, and not a little</h2>"
            "<p>Samarkand and Bukhara regularly hit 38–40°C (100–104°F) in July and "
            "August. It's still doable — mornings and evenings are fine, and sites "
            "have shaded courtyards — but you'll want to structure the day around "
            "the heat rather than ignore it. This is also when Amirsoy and Chimgan "
            "earn their place on an itinerary: the mountains run noticeably cooler "
            "than the cities.</p>"
            "<h2>Autumn (September–early November): the other good window</h2>"
            "<p>Our other recommended season, and arguably slightly better than "
            "spring for photography — softer light, harvest season in the "
            "countryside, and temperatures easing back into a comfortable range by "
            "mid-September.</p>"
            "<h2>Winter (December–February): quiet, cold, and cheaper</h2>"
            "<p>Genuinely cold, sometimes with snow in Tashkent and the mountains "
            "(good news if you're going to Amirsoy specifically for skiing). Fewer "
            "tourists, shorter days, but the monuments themselves don't go anywhere "
            "— if you don't mind bundling up, it's a legitimately quiet way to see "
            "the Silk Road cities without the crowds.</p>"
            "<h2>Our take</h2>"
            "<p>If your dates are flexible at all, aim for late April–May or "
            "September–October. If they're not, it's still a good trip in summer or "
            "winter — it just changes the pace and what you'll want to wear, and "
            "we'll tell you honestly if a specific week looks uncomfortable when you "
            "send us your dates.</p>"
        ),
        "body_ru": (
            "<p>Узбекистан находится глубоко в глубине материка, без моря, "
            "смягчающего перепады температур — поэтому разница между поездкой в мае "
            "и поездкой в июле гораздо заметнее, чем ожидают многие туристы, "
            "впервые приезжающие в страну.</p>"
            "<h2>Весна (апрель — начало июня): лучшее время в целом</h2>"
            "<p>Это сезон, который мы рекомендуем чаще всего. Дневная температура "
            "комфортна для многочасовых прогулок по Регистану или Ичан-Кале, "
            "природа зеленеет, а пик летнего наплыва туристов ещё не наступил.</p>"
            "<h2>Лето (середина июня — август): жарко, и весьма</h2>"
            "<p>В Самарканде и Бухаре в июле и августе регулярно бывает 38–40°C. "
            "Путешествовать всё ещё можно — утро и вечер комфортны, а у "
            "достопримечательностей есть тенистые дворы — но день стоит строить "
            "вокруг жары, а не игнорировать её. Именно в это время в маршруте особенно "
            "хорошо смотрятся Амирсой и Чимган: в горах заметно прохладнее, чем в "
            "городах.</p>"
            "<h2>Осень (сентябрь — начало ноября): второе хорошее окно</h2>"
            "<p>Наш второй рекомендуемый сезон, и для фотографии он, пожалуй, даже "
            "немного лучше весны — мягкий свет, время сбора урожая в сельской "
            "местности, а температура к середине сентября снова становится "
            "комфортной.</p>"
            "<h2>Зима (декабрь — февраль): тихо, холодно и дешевле</h2>"
            "<p>По-настоящему холодно, иногда со снегом в Ташкенте и в горах "
            "(хорошая новость, если вы едете в Амирсой именно ради катания на "
            "лыжах). Туристов меньше, дни короче, но памятники никуда не деваются — "
            "если не против тепло одеться, это по-настоящему тихий способ увидеть "
            "города Шёлкового пути без толп.</p>"
            "<h2>Наш совет</h2>"
            "<p>Если даты хоть немного гибкие, ориентируйтесь на конец апреля — май "
            "или сентябрь — октябрь. Если нет — поездка будет хорошей и летом, и "
            "зимой, просто изменится темп и то, что стоит взять с собой в поездку; "
            "мы честно скажем, если конкретная неделя окажется некомфортной, когда "
            "вы пришлёте нам даты.</p>"
        ),
        "related_destinations": ["amirsoy-chimgan"],
    },
    {
        "title": "Samarkand vs Bukhara vs Khiva: Which Silk Road City Should You Visit First?",
        "title_ru": "Самарканд, Бухара или Хива: с какого города Шёлкового пути начать?",
        "excerpt": (
            "If you only have time for one Silk Road city, here's how the three "
            "classic stops actually differ — in scale, pace and what a day there "
            "feels like."
        ),
        "excerpt_ru": (
            "Если время позволяет посетить только один город Шёлкового пути — "
            "разбираем, чем на самом деле отличаются три классические "
            "остановки: масштабом, темпом и ощущением от дня в городе."
        ),
        "author": "Abdulloh Tours",
        "category": "Destinations",
        "published_at": datetime(2026, 3, 17, 9, 0, tzinfo=UTC),
        "meta_title": "Samarkand vs Bukhara vs Khiva Compared",
        "meta_description": (
            "Registan grandeur, Bukhara's walkable old town, or Khiva's complete "
            "walled city — a practical comparison for a first-time Uzbekistan trip."
        ),
        "body": (
            "<p>All three cities were Silk Road stops, all three have UNESCO-listed "
            "old towns, and all three get compared to each other constantly — but "
            "they're genuinely different experiences, not three versions of the same "
            "thing.</p>"
            "<h2>Samarkand: monumental, spread out, unmissable</h2>"
            "<p>Samarkand is the one people have usually heard of before they arrive, "
            "and the Registan lives up to it — three enormous madrasahs facing each "
            "other across a public square, at a scale photos undersell. The "
            "trade-off is that the sites are spread across a modern city, so you're "
            "moving between them by vehicle rather than wandering on foot. Budget "
            "two full days.</p>"
            "<h2>Bukhara: compact, walkable, easier to settle into</h2>"
            "<p>Where Samarkand is monumental, Bukhara is dense — the old town "
            "survives largely intact, and most of what you'll want to see is within "
            "a fifteen-minute walk of the Lyab-i Hauz pool. It's a better fit if you "
            "want to wander without a fixed plan for an afternoon, and a good second "
            "stop after a more structured day in Samarkand.</p>"
            "<h2>Khiva: complete, quiet, a little further out</h2>"
            "<p>Khiva's old town, Itchan Kala, is the most cohesive of the three — "
            "the whole walled city is preserved as a single site, small enough to "
            "cross on foot in twenty minutes. It's also the furthest from Tashkent, "
            "which keeps it quieter but means it's usually the last stop on a "
            "longer itinerary rather than a quick add-on.</p>"
            "<h2>So which one first?</h2>"
            "<p>If you only have three or four days total, Samarkand and Bukhara "
            "together make the strongest short itinerary — see our "
            '<a href="/en/tours/silk-road-highlights/">Silk Road Highlights</a> '
            "route. If you have a week or more, add Khiva; it's the one people "
            "regret skipping, not the one they regret including.</p>"
        ),
        "body_ru": (
            "<p>Все три города были остановками на Шёлковом пути, у всех трёх старые "
            "города внесены в список ЮНЕСКО, и их постоянно сравнивают друг с "
            "другом — но по ощущениям это по-настоящему разный опыт, а не три "
            "варианта одного и того же.</p>"
            "<h2>Самарканд: монументальный, растянутый, обязательный к посещению</h2>"
            "<p>О Самарканде обычно уже слышали до приезда, и Регистан полностью "
            "оправдывает ожидания — три огромных медресе, обращённых друг к другу "
            "через площадь, в масштабе, который фотографии передают не полностью. "
            "Обратная сторона в том, что объекты разбросаны по современному городу, "
            "поэтому между ними перемещаются на транспорте, а не пешком. "
            "Закладывайте два полных дня.</p>"
            "<h2>Бухара: компактная, пешеходная, проще освоиться</h2>"
            "<p>Если Самарканд монументален, то Бухара плотная — старый город "
            "сохранился почти целиком, и большая часть того, что стоит увидеть, "
            "находится в пятнадцати минутах ходьбы от пруда Ляби-Хауз. Это лучший "
            "вариант, если хочется просто побродить без чёткого плана на "
            "полдня, и хорошая вторая остановка после более насыщенного дня в "
            "Самарканде.</p>"
            "<h2>Хива: цельная, тихая, чуть дальше</h2>"
            "<p>Старый город Хивы, Ичан-Кала, самый цельный из трёх — весь "
            "обнесённый стеной город сохранён как единый объект, достаточно "
            "небольшой, чтобы пересечь его пешком за двадцать минут. Это и самый "
            "дальний город от Ташкента, поэтому здесь тише, но обычно он становится "
            "последней точкой более длинного маршрута, а не быстрым дополнением.</p>"
            "<h2>Так с какого начать?</h2>"
            "<p>Если в запасе всего три-четыре дня, Самарканд и Бухара вместе дают "
            "самый сильный короткий маршрут — см. наш тур "
            '<a href="/ru/tours/silk-road-highlights/">«Жемчужины Шёлкового '
            "пути»</a>. Если есть неделя и больше — добавьте Хиву: обычно жалеют "
            "именно о том, что её пропустили, а не о том, что включили.</p>"
        ),
        "related_destinations": ["samarkand", "bukhara", "khiva"],
        "related_packages": ["silk-road-highlights"],
    },
    {
        "title": "What to Pack for Uzbekistan: A Practical Packing List",
        "title_ru": "Что взять с собой в Узбекистан: практичный список вещей",
        "excerpt": (
            "Dust, sun, dress codes at religious sites, and a climate that swings "
            "hard between day and night — here's what actually earns a spot in "
            "your bag."
        ),
        "excerpt_ru": (
            "Пыль, солнце, дресс-код у религиозных объектов и климат с резкими "
            "перепадами между днём и ночью — разбираем, что действительно стоит "
            "взять с собой."
        ),
        "author": "Abdulloh Tours",
        "category": "Tips",
        "published_at": datetime(2026, 3, 24, 9, 0, tzinfo=UTC),
        "meta_title": "Uzbekistan Packing List: What You Actually Need",
        "meta_description": (
            "A practical Uzbekistan packing list — clothing for mosque/madrasah "
            "visits, sun protection, and what to leave at home."
        ),
        "body": (
            "<p>Uzbekistan doesn't require anything exotic, but a few things are "
            "easy to get wrong if you've packed for a generic warm-weather trip "
            "instead of this specific climate and these specific sites.</p>"
            "<h2>Clothing for mosques and madrasahs</h2>"
            "<p>Most historic sites don't enforce a strict dress code the way some "
            "active mosques elsewhere do, but covered shoulders and knees are the "
            "respectful default, and you'll be glad of the sun protection anyway. "
            "A light scarf is useful for women visiting a handful of stricter sites.</p>"
            "<h2>Footwear: comfort over style</h2>"
            "<p>You'll be walking on uneven stone and brick for hours at a time — "
            "Registan's courtyards, Itchan Kala's streets, Bukhara's old town. "
            "Broken-in walking shoes matter more than anything else on this list.</p>"
            "<h2>Sun protection, taken seriously</h2>"
            "<p>Central Asian sun is stronger than it looks, especially April "
            "through September. Sunscreen, a hat, and sunglasses aren't optional "
            "extras here.</p>"
            "<h2>Layers, because of the day/night swing</h2>"
            "<p>Even in summer, desert nights cool down noticeably. Spring and "
            "autumn days can be warm with genuinely cold evenings. A packable layer "
            "earns its space in the bag in every season except peak summer.</p>"
            "<h2>Small things worth bringing</h2>"
            "<ul>"
            "<li>A basic first-aid kit and any prescription medication you need — "
            "pharmacies exist but brands differ</li>"
            "<li>A portable charger — long driving days between cities are a good "
            "time to run devices down</li>"
            "<li>Cash in small denominations for markets and smaller sites that "
            "don't take cards</li>"
            "</ul>"
            "<p>Beyond that, pack light — our vehicles handle the driving, and a "
            "smaller bag makes hotel check-ins and city walks easier.</p>"
        ),
        "body_ru": (
            "<p>Для поездки в Узбекистан не нужно ничего экзотического, но легко "
            "ошибиться, если собирать вещи как для обычной поездки в тёплую страну, "
            "а не под конкретный климат и конкретные объекты.</p>"
            "<h2>Одежда для мечетей и медресе</h2>"
            "<p>Большинство исторических объектов не требует строгого дресс-кода, "
            "как некоторые действующие мечети в других странах, но закрытые плечи и "
            "колени — уважительный вариант по умолчанию, да и от солнца они защищают. "
            "Лёгкий платок пригодится женщинам при посещении нескольких более "
            "строгих объектов.</p>"
            "<h2>Обувь: удобство важнее внешнего вида</h2>"
            "<p>Ходить придётся часами по неровному камню и кирпичу — дворы "
            "Регистана, улицы Ичан-Калы, старый город Бухары. Разношенная удобная "
            "обувь важнее всего остального в этом списке.</p>"
            "<h2>Защита от солнца — не мелочь</h2>"
            "<p>Солнце в Центральной Азии сильнее, чем кажется, особенно с апреля по "
            "сентябрь. Солнцезащитный крем, головной убор и очки — не "
            "необязательные мелочи.</p>"
            "<h2>Слои одежды из-за перепада температур день/ночь</h2>"
            "<p>Даже летом пустынные ночи заметно холодают. Весной и осенью днём "
            "может быть тепло, а вечером — по-настоящему холодно. Компактный тёплый "
            "слой пригодится в любой сезон, кроме разгара лета.</p>"
            "<h2>Мелочи, которые стоит взять</h2>"
            "<ul>"
            "<li>Базовую аптечку и рецептурные лекарства при необходимости — аптеки "
            "есть, но марки препаратов отличаются</li>"
            "<li>Портативное зарядное устройство — долгие переезды между городами "
            "хорошо подходят для подзарядки устройств</li>"
            "<li>Наличные небольшими купюрами для рынков и небольших объектов, где "
            "не принимают карты</li>"
            "</ul>"
            "<p>В остальном — собирайтесь налегке: за руль садимся мы, а с небольшой "
            "сумкой проще заселяться в отели и гулять по городу.</p>"
        ),
    },
    {
        "title": "Is Uzbekistan Safe for Tourists? What to Actually Expect",
        "title_ru": "Безопасен ли Узбекистан для туристов? Чего ожидать на самом деле",
        "excerpt": (
            "A direct, non-alarmist answer to the question we get most often from "
            "first-time visitors, especially those travelling solo."
        ),
        "excerpt_ru": (
            "Прямой, без лишней тревожности ответ на вопрос, который нам задают "
            "чаще всего — особенно те, кто путешествует в одиночку."
        ),
        "author": "Abdulloh Tours",
        "category": "Tips",
        "published_at": datetime(2026, 3, 31, 9, 0, tzinfo=UTC),
        "meta_title": "Is Uzbekistan Safe? A Practical Answer",
        "meta_description": (
            "Uzbekistan safety for tourists, explained practically — crime, solo "
            "travel, scams, and what a private driver actually changes."
        ),
        "body": (
            "<p>This is close to the most common question we get from people who "
            "haven't been to Central Asia before, so we'll answer it plainly: "
            "Uzbekistan is a genuinely safe country to visit, including for solo "
            "travellers and solo women, and the concerns most first-time visitors "
            "bring with them are usually outdated.</p>"
            "<h2>Violent crime against tourists is rare</h2>"
            "<p>Uzbekistan has tightened tourism infrastructure significantly over "
            "the past decade, and violent crime targeting foreign visitors is "
            "genuinely uncommon in the cities on a typical itinerary. Normal travel "
            "sense — watch your belongings in crowded bazaars, don't flash large "
            "amounts of cash — is enough.</p>"
            "<h2>The more realistic risk is minor overcharging</h2>"
            "<p>The most likely thing to actually happen to you is a taxi or market "
            "stall quoting a higher price to an obvious tourist, not anything more "
            "serious. It's an annoyance, not a danger — and it's one of the reasons "
            "people book a driver rather than negotiating transport themselves at "
            "every stop.</p>"
            "<h2>What a private driver actually changes</h2>"
            "<p>Beyond convenience, having a driver removes most of the situations "
            "where petty issues happen in the first place: no negotiating taxis at "
            "train stations, no guessing which bus goes where, no walking through "
            "an unfamiliar area after dark looking for a hotel. It's less about "
            "danger and more about removing friction.</p>"
            "<h2>Solo travellers, including women travelling alone</h2>"
            "<p>Solo women travellers regularly visit Uzbekistan without incident, "
            "and locals are generally helpful rather than intrusive toward "
            "tourists. Standard precautions apply — as they would anywhere — but "
            "this isn't a destination that requires special safety planning beyond "
            "that.</p>"
            "<h2>Our honest bottom line</h2>"
            "<p>We wouldn't run this business, or send our own families through "
            "these routes, if we thought otherwise. If something specific is "
            "worrying you about your particular trip, ask us directly — we'd "
            "rather answer a real question than have you find an outdated forum "
            "post instead.</p>"
        ),
        "body_ru": (
            "<p>Это едва ли не самый частый вопрос от тех, кто раньше не бывал в "
            "Центральной Азии, поэтому ответим прямо: Узбекистан — по-настоящему "
            "безопасная страна для поездки, включая одиночных путешественников и "
            "женщин, путешествующих в одиночку, а опасения, с которыми обычно "
            "приезжают новички, чаще всего устарели.</p>"
            "<h2>Насильственные преступления против туристов — редкость</h2>"
            "<p>За последнее десятилетие Узбекистан существенно укрепил туристическую "
            "инфраструктуру, и насильственные преступления в отношении иностранных "
            "гостей в городах типичного маршрута действительно редки. Достаточно "
            "обычной туристической осторожности — следить за вещами на людных "
            "базарах, не демонстрировать крупные суммы наличных.</p>"
            "<h2>Более реальный риск — небольшая переплата</h2>"
            "<p>Скорее всего с вами случится то, что таксист или продавец на рынке "
            "назовёт цену повыше явному туристу — а не что-то более серьёзное. Это "
            "раздражает, но не опасно, и как раз поэтому многие предпочитают "
            "нанять водителя, а не договариваться о транспорте самостоятельно на "
            "каждой остановке.</p>"
            "<h2>Что на самом деле меняет частный водитель</h2>"
            "<p>Помимо удобства, водитель убирает саму ситуацию, в которой обычно "
            "возникают мелкие неприятности: не нужно торговаться с таксистами на "
            "вокзалах, угадывать нужный автобус или искать отель пешком по "
            "незнакомому району в темноте. Дело не столько в опасности, сколько в "
            "устранении лишних сложностей.</p>"
            "<h2>Одиночные путешественники, включая женщин</h2>"
            "<p>Женщины регулярно путешествуют по Узбекистану в одиночку без "
            "каких-либо инцидентов, а местные жители в целом скорее помогают "
            "туристам, чем докучают им. Действуют обычные меры предосторожности — "
            "как и в любой другой стране, — но это направление не требует особого "
            "плана безопасности сверх этого.</p>"
            "<h2>Наш честный вывод</h2>"
            "<p>Мы бы не занимались этим бизнесом и не отправляли бы по этим "
            "маршрутам собственные семьи, если бы думали иначе. Если конкретно вас "
            "что-то беспокоит по поводу вашей поездки — спросите нас напрямую: нам "
            "проще ответить на реальный вопрос, чем позволить вам наткнуться на "
            "устаревший пост на форуме.</p>"
        ),
    },
]

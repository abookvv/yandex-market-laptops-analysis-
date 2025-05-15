import streamlit as st
import pandas as pd
import os
import altair as alt

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'clean_dataset_parsing_laptops_on_yand_market.csv')

st.title("Анализ ноутбуков с Яндекс.Маркета")
menu = st.sidebar.selectbox("Навигация", ["Главная", "Данные", "EDA (первичный анализ)", "Тренды & закономерности", "Выводы & рекомендации"])

@st.cache
def load_data(path):
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {e}")
        return pd.DataFrame()
df = load_data(DATA_PATH)

df = load_data(DATA_PATH)
if menu == "Главная":
    st.header("Главная")
    st.subheader("Выполнили:")
    st.write("Медведев Арсений Сергеевич 466676")
    st.write("Бунковская Анна Вячеславовна 465304")
    st.write("Данные собраны с Яндекс.Маркета с помощью парсера, доступен анализ и визуализации.")
    st.header("Шаги по реализации проекта")
    st.write("1. Парсинг данных с Яндекс маркет + разобраться, что делать с их ограниченным API")
    st.write("2. Перевести данные в таблице в нужный фомат (числа должны быть float или int, а не str)")
    st.write("3. Предварительный анализ данных")
    st.write("4. Очитска данных от пропусков, дубликатов, выбросов по цене и удаление не релевантных данных")
    st.write("5. Создание визуализации и проведение анализа ноутбуков")
    st.write("6. Создание дешборда с помощью Streamlit и добавление графиков, анализ и выводы в него")
elif menu == "Данные":
    st.header("Данные")
    if df.empty:
        st.write("Данные не загружены.")
    else:
        # Показать интерактивную таблицу
        st.subheader("Таблица данных")
        st.write("В таблице имеются данные о названии ноутбука, характеристики (about), цена, рейтинг, количество отзывов и ссылка")
        st.dataframe(df)
        # Счётчики
        st.subheader("Основные характеристики данных")
        col1, col2, col3 = st.columns(3)
        col1.metric("Общее число записей", len(df))
        col2.metric("Количество пропусков", df.isnull().sum().sum())
        # Здесь пример категории, замените на свою реальную категорию, если есть
        if 'category' in df.columns:
            dist = df['category'].value_counts().reset_index()
            dist.columns = ['Категория', 'Количество']
            col3.metric("Уникальных категорий", dist.shape[0])
            st.bar_chart(df['category'].value_counts())
elif menu == "EDA (первичный анализ)":
    st.header("EDA (Первичный анализ)")
    if df.empty:
        st.write("Данные не загружены.")
    else:
        st.subheader("Анализ числовых переменных")
        numeric_cols = ['price', 'rating', 'reviews']
        for col in numeric_cols:
            if col in df.columns:
                median = df[col].median()
                mean = df[col].mean()
                std = df[col].std()
                min_val = df[col].min()
                max_val = df[col].max()
                zero_count = (df[col] == 0).sum()
                st.markdown(f"**Столбец `{col}`:**")
                st.markdown(f"- Медиана: {median:.2f}")
                st.markdown(f"- Среднее: {mean:.2f}")
                st.markdown(f"- Стандартное отклонение: {std:.2f}")
                st.markdown(f"- Минимум: {min_val}")
                st.markdown(f"- Максимум: {max_val}")
                st.markdown(f"- Количество нулевых значений: {zero_count}")
            else:
                st.markdown(f"Столбец `{col}` отсутствует в данных.")
        # Пример: гистограмма по цене (если есть столбец 'price')

        st.subheader("Распределение цен")
        chart = alt.Chart(df).mark_bar().encode(
            alt.X("price:Q", bin=alt.Bin(maxbins=50), title="Цена"),
            y='count()'
        ).properties(width=700, height=400)
        st.altair_chart(chart)
        st.write("Больше всего ноутбуков от 25 до 80 тыс, что примерно эквивалентно среднему классу")

        st.subheader("График зависимости цены от рейтинга:")
        rating_min = df['rating'].min()
        rating_max = df['rating'].max()
        scatter = alt.Chart(df).mark_circle(opacity=0.5, color='green').encode(
            x=alt.X('rating:Q', title='Рейтинг (из 5)',
                    scale=alt.Scale(domain=[rating_min, rating_max])),
            y=alt.Y('price:Q', title='Цена (руб)'),
            tooltip=['rating', 'price']
        ).properties(
            width=700,
            height=400,
            title='Зависимость цены от рейтинга'
        )
        st.altair_chart(scatter)
        correlation = df[['price', 'rating']].corr().iloc[0, 1]
        st.write(f"Коэффициент корреляции: {correlation:.2f}")
        st.write("Наблюдается слабая положительная корреляция между ценой и рейтингом. Более дорогие ноутбуки вероятно более качественные")

        st.subheader("График зависимости цены от рейтинга и количества отзывов:")
        # Нормализация размера пузырей
        max_reviews = df['reviews'].max()
        size_scale = 1000  # Масштабирующий коэффициент
        bubble_chart = alt.Chart(df).mark_circle(opacity=0.5, color='blue', stroke='black', strokeWidth=0.5).encode(
            x=alt.X('rating:Q', title='Рейтинг (1-5)',
                    scale=alt.Scale(domain=[df['rating'].min(), df['rating'].max()])),
            y=alt.Y('price:Q', title='Цена (руб)'),
            size=alt.Size('reviews:Q', title='Количество отзывов',
                          scale=alt.Scale(domain=[0, max_reviews], range=[0, size_scale])),
            tooltip=['rating', 'price', 'reviews']
        ).properties(
            width=700,
            height=400,
            title='Зависимость цены от рейтинга и количества отзывов'
        )
        st.altair_chart(bubble_chart)
        st.write("Пик количества отзывов приходится на ценовой диапазон 50-80 тыс. руб, так как к этому сегменту относятся ноутбуки среднего класса и их чаще покуапют")
        # Находим ноутбуки с рейтингом 4.8+ и ценой ниже 40 тыс. руб.
        anomalies = df[(df['rating'] >= 4.8) & (df['price'] < 40_000)]
        # Доля таких ноутбуков от общего числа
        anomaly_percentage = len(anomalies) / len(df) * 100
        st.write(f"Доля аномалий: {anomaly_percentage:.1f}%")
        st.write("Около 14% ноутбуков с рейтингом 4.8+ имеют подозрительно низкую цену (<40 тыс. руб.). Это могу быть 'накрученные' отзывы или ошибки")
        st.write("Лучшее соотношение всех 3 составляюищих:")
        st.write("Цена: 65-90 тыс. руб.")
        st.write("Рейтинг: 4.4-4.9")
        st.write("Отзывов: 50-300")

elif menu == "Тренды & закономерности":
    st.header("Тренды & закономерности")
    st.write("Тут можно настроить параметры по своим предпочтением относительно цены, рейтинга и количества отзывов. Снижу представлена табличка от лучших к худшим ноутбукам по вашему зщапросу")
    if df.empty:
        st.write("Данные не загружены.")
    else:
        # Фильтры для примера по дате, если есть поле 'date' в формате datetime
        filtered_df = df

        st.subheader("Выбор лучших ноутбуков по параметрам")
        # Проверяем, что необходимые столбцы есть
        if all(col in filtered_df.columns for col in ['price', 'rating', 'reviews']):
            min_price = int(filtered_df['price'].min())
            max_price = int(filtered_df['price'].max())
            min_rating = float(filtered_df['rating'].min())
            max_rating = float(filtered_df['rating'].max())
            min_reviews = int(filtered_df['reviews'].min())
            max_reviews = int(filtered_df['reviews'].max())
            price_range = st.slider("Цена", min_price, max_price, (min_price, max_price))
            rating_range = st.slider("Рейтинг", min_rating, max_rating, (min_rating, max_rating))
            reviews_range = st.slider("Количество отзывов", min_reviews, max_reviews, (min_reviews, max_reviews))
            filtered_best = filtered_df[
                (filtered_df['price'] >= price_range[0]) & (filtered_df['price'] <= price_range[1]) &
                (filtered_df['rating'] >= rating_range[0]) & (filtered_df['rating'] <= rating_range[1]) &
                (filtered_df['reviews'] >= reviews_range[0]) & (filtered_df['reviews'] <= reviews_range[1])
                ]
            st.write(f"Найдено ноутбуков: {len(filtered_best)}")
            top_laptops = filtered_best.sort_values(by=['rating', 'reviews'], ascending=[False, False]).head(20)
            st.dataframe(top_laptops.reset_index(drop=True))
        else:
            st.write("В данных не найдены необходимые столбцы: 'price', 'rating', 'reviews'.")

        st.write(f"Отображено записей после фильтрации: {len(filtered_df)}")
        # Визуализация — пример: средняя цена по категориям
        if 'category' in df.columns and 'price' in df.columns:
            grouped = filtered_df.groupby('category')['price'].mean().reset_index()
            bar_chart = alt.Chart(grouped).mark_bar().encode(
                x='category:N',
                y='price:Q',
                tooltip=['category', 'price']
            ).properties(width=700, height=400)
            st.altair_chart(bar_chart)


elif menu == "Выводы & рекомендации":
    st.header("Выводы & рекомендации")
    st.markdown("""
    ### Ключевые инсайты
    - Анализ распределения цен показал, что большинство ноутбуков находятся в среднем ценовом диапазоне. Это может указывать на то, что рынок ноутбуков в основном ориентирован на средний класс, с меньшим количеством моделей в низком и высоком ценовых сегментах. 
    - Наибольшее количество отзывов у ноутбуков среднего класса, поэтому это количество не самая объективная оценка
    - График зависимости цены от рейтинга показал положительную корреляцию между этими переменными. Ноутбуки с более высокими рейтингами, как правило, имеют более высокие цены
    - Пузырьковая диаграмма, отображающая зависимость цены от рейтинга и количества отзывов, показала, что модели с большим количеством отзывов имеют тенденцию к более высоким ценам.
    ### В разработке
    - В будущем можно провести более глубокий анализ, включая исследование влияния других факторов, таких как бренд, характеристики (процессор, объем оперативной памяти и т.д.) и сезонные колебания цен.
    - Добавить скрол и выбор по новым категориям
    - Провести более глубокий анализ собирая боьлшее количество данных
    - Парсить данные с большего количества маркетплейсов
    """)

import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import logging

# Configuración del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Función para cargar los datos desde los archivos CSV
def load_data():
    # Rutas a los archivos CSV
    orders_file = os.path.join('scripts', 'orders_with_products.csv')
    products_file = os.path.join('scripts', 'all_products.csv')
    
    # Cargar archivos CSV
    try:
        combined_df = pd.read_csv(orders_file)
        products_df = pd.read_csv(products_file)
        return combined_df, products_df
    except FileNotFoundError:
        st.error(f"No se encontró el archivo CSV. Verifica la ruta: {orders_file} o {products_file}")

# Función para mostrar el gráfico de barras horizontal
def show_horizontal_bar_chart(df, x_column, y_column, title):
    fig = px.bar(df, x=x_column, y=y_column, orientation='h', title=title)
    st.plotly_chart(fig)

# Función para mostrar el gráfico de barras vertical
def show_vertical_bar_chart(df, x_column, y_column, title):
    fig = px.bar(df, x=x_column, y=y_column, title=title)
    st.plotly_chart(fig)

# Función para mostrar el gráfico de pastel
def show_pie_chart(df, labels_column, values_column, title):
    fig = px.pie(df, names=labels_column, values=values_column, title=title)
    st.plotly_chart(fig)

# Función principal de la aplicación Streamlit
def main():
    # Cargar los datos
    combined_df, products_df = load_data()

    # 1. Producto más comprado (Gráfico de barras horizontal)
    most_purchased_products = combined_df.groupby('product_id')['quantity'].sum().nlargest(10).reset_index()
    most_purchased_products_df = pd.merge(most_purchased_products, products_df[['objectID', 'name']], left_on='product_id', right_on='objectID', how='left')
    most_purchased_products_df = most_purchased_products_df.rename(columns={'quantity': 'Cantidad total vendida'})

    # Mostrar el gráfico de barras horizontal con nombres de productos
    show_horizontal_bar_chart(most_purchased_products_df, 'Cantidad total vendida', 'name', 'Producto más comprado')

    # 2. Categoría de producto más popular (Gráfico de barras vertical)
    category_sales = combined_df.groupby('categories')['quantity'].sum().nlargest(10).reset_index()
    category_sales_df = category_sales.rename(columns={'quantity': 'Cantidad total vendida'})
    
    show_vertical_bar_chart(category_sales_df, 'categories', 'Cantidad total vendida', 'Categoría de producto más popular')

    # 3. Cliente que ha realizado más compras (Gráfico de barras horizontal)
    # Contar la cantidad de órdenes únicas por cliente
    unique_orders_by_customer = combined_df.groupby('customer_id')['order_id'].nunique().nlargest(10).reset_index()
    unique_orders_by_customer = unique_orders_by_customer.rename(columns={'order_id': 'Cantidad de compras únicas'})

    # Mostrar el gráfico de barras horizontal
    show_horizontal_bar_chart(unique_orders_by_customer, 'Cantidad de compras únicas', 'customer_id', 'Cliente que ha realizado más compras')

    # 4. Cantidad total gastada por el cliente que más ha gastado (Gráfico de barras vertical)
    # Asegurarnos de que la columna 'payment' sea numérica
    combined_df['payment'] = pd.to_numeric(combined_df['payment'], errors='coerce')
    # Agrupar por customer_id y order_id, luego sumar los pagos para cada orden única
    total_spent_per_order = combined_df.groupby(['customer_id', 'order_id'])['payment'].sum().reset_index()
    total_spent_by_customer = total_spent_per_order.groupby('customer_id')['payment'].sum().nlargest(10).reset_index()
    total_spent_by_customer = total_spent_by_customer.rename(columns={'payment': 'Cantidad total gastada'})

    # Mostrar el gráfico de barras vertical
    show_vertical_bar_chart(total_spent_by_customer, 'customer_id', 'Cantidad total gastada', 'Cantidad total gastada por el cliente que más ha gastado')

    # 5. Calificación promedio de los productos comprados (Gráfico de barras vertical)
    most_purchased_product_ids = most_purchased_products_df['product_id']
    avg_rating_per_product = products_df[products_df['objectID'].isin(most_purchased_product_ids)].groupby('name')['rating'].mean().nlargest(10).reset_index()
    avg_rating_per_product_df = pd.DataFrame({'name': avg_rating_per_product['name'],
                                              'Calificación promedio': avg_rating_per_product['rating']})
    show_vertical_bar_chart(avg_rating_per_product_df, 'name', 'Calificación promedio', 'Calificación promedio de los productos comprados')

    # 6. Distribución de los métodos de pago utilizados (Gráfico de pastel)
    payment_distribution = combined_df['payment_type'].value_counts()
    payment_distribution_df = pd.DataFrame({'Método de pago': payment_distribution.index,
                                            'Cantidad de compras': payment_distribution.values})
    show_pie_chart(payment_distribution_df, 'Método de pago', 'Cantidad de compras', 'Distribución de los métodos de pago utilizados')

    # 7. Ciudad con más compras realizadas (Gráfico de pastel)
    city_sales = combined_df['customer_city'].value_counts().head(10)
    city_sales_df = pd.DataFrame({'Ciudad': city_sales.index,
                                  'Cantidad de compras': city_sales.values})
    show_pie_chart(city_sales_df, 'Ciudad', 'Cantidad de compras', 'Ciudad con más compras realizadas')

    # Agrupar por estado de la orden y contar el número de registros
    order_status_counts = combined_df['order_status'].value_counts()

    # Calcular porcentaje de cada estado respecto al total
    total_orders = order_status_counts.sum()
    order_status_perc = order_status_counts / total_orders * 100

    # Crear un DataFrame para el gráfico
    order_status_df = pd.DataFrame({'order_status': order_status_perc.index, 'percentage': order_status_perc.values})

    # Ordenar porcentaje descendente para el gráfico
    order_status_df = order_status_df.sort_values(by='percentage', ascending=False)

    # Crear el gráfico de barras apiladas (stacked bar chart) con Plotly
    fig = go.Figure()

    # Añadir una sola barra apilada con los porcentajes
    fig.add_trace(go.Bar(
        x=order_status_df['order_status'],
        y=order_status_df['percentage'],
        text=order_status_df['percentage'].round(2),
        textposition='auto',
        hoverinfo='text',
        marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']  # Colores por defecto
    ))

    # Configurar el diseño del gráfico
    fig.update_layout(
        title='Tasa de estado de las órdenes',
        xaxis_title='Estado de la orden',
        yaxis_title='Porcentaje (%)',
        showlegend=False,  # No mostrar la leyenda
        uniformtext_minsize=8,  # Tamaño mínimo de texto uniforme
        uniformtext_mode='hide'  # Ocultar texto si no cabe
    )

    st.plotly_chart(fig)
    # 9. Peso promedio de los productos comprados (Gráfico de barras vertical)
    # Obtener los productos más comprados
    most_purchased_product_ids = combined_df['product_id'].value_counts().nlargest(10).index

    # Filtrar combined_df para obtener información de los productos más comprados
    filtered_products_df = combined_df[combined_df['product_id'].isin(most_purchased_product_ids)]

    # Calcular el peso promedio por producto
    average_weight_per_product = filtered_products_df.groupby('product_id')['product_weight_g'].mean().reset_index()

    # Fusionar con la información de productos para obtener nombres y pesos promedio
    most_purchased_products_df = pd.merge(average_weight_per_product, products_df[['objectID', 'name']], left_on='product_id', right_on='objectID', how='left')
    most_purchased_products_df = most_purchased_products_df.rename(columns={'product_weight_g': 'Peso promedio'})

    # Mostrar el gráfico de barras vertical con nombres de productos
    show_vertical_bar_chart(most_purchased_products_df, 'name', 'Peso promedio', 'Peso promedio de los productos más comprados')

    # 10. Ventas a lo largo del tiempo (Serie de tiempo - gráfico de líneas)
    combined_df['timestamp'] = pd.to_datetime(combined_df['timestamp'])
    monthly_sales = combined_df.resample('M', on='timestamp')['order_id'].count()
    monthly_sales_df = pd.DataFrame({'Fecha': monthly_sales.index, 'Cantidad de compras': monthly_sales.values})
    fig = px.line(monthly_sales_df, x='Fecha', y='Cantidad de compras', title='Ventas a lo largo del tiempo')
    st.plotly_chart(fig)

# Punto de entrada para ejecutar la aplicación
if __name__ == '__main__':
    main()

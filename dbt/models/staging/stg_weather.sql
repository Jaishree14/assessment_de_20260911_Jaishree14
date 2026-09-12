with source as (
    select * from {{ source('raw', 'weather_daily') }}
),

renamed as (
    select
        city,
        logical_date,
        date as weather_date,
        city || '_' || date::text as city_date_key,
        temperature_2m_max as temp_max_c,
        temperature_2m_min as temp_min_c,
        precipitation_sum as precipitation_mm
    from source
)

select * from renamed
REGISTER 'lib/datafu-pig-1.6.1.jar';

DEFINE Median datafu.pig.stats.StreamingMedian();

raw_clicks = LOAD 'data/raw/train_sample.csv'
    USING PigStorage(',')
    AS (
        ip:chararray,
        app:int,
        device:int,
        os:int,
        channel:int,
        click_time:chararray,
        attributed_time:chararray,
        is_attributed:int
    );

-- Loại bỏ header CSV
clicks = FILTER raw_clicks BY ip IS NOT NULL AND ip != 'ip';

-- Feature theo IP
by_ip = GROUP clicks BY ip;

ip_features = FOREACH by_ip {
    unique_apps = DISTINCT clicks.app;
    unique_channels = DISTINCT clicks.channel;

    GENERATE
        group AS ip,
        COUNT(clicks) AS click_count,
        COUNT(unique_apps) AS unique_app_count,
        COUNT(unique_channels) AS unique_channel_count,
        SUM(clicks.is_attributed) AS conversions,
        Median(clicks.app) AS median_app_id;
};

scored_ips = FOREACH ip_features GENERATE
    ip,
    click_count,
    unique_app_count,
    unique_channel_count,
    conversions,
    median_app_id,

    (int)(
        (click_count >= 30 ? 50 : (click_count >= 10 ? 30 : 0))
        + ((conversions == 0 AND click_count >= 5) ? 25 : 0)
        + ((unique_app_count <= 2 AND click_count >= 5) ? 15 : 0)
        + ((unique_channel_count <= 2 AND click_count >= 5) ? 10 : 0)
    ) AS risk_score;

ip_risk = FOREACH scored_ips GENERATE
    ip,
    click_count,
    unique_app_count,
    unique_channel_count,
    conversions,
    median_app_id,
    risk_score,
    (risk_score >= 70 ? 'HIGH_RISK' :
        (risk_score >= 40 ? 'MEDIUM_RISK' : 'LOW_RISK')
    ) AS risk_label;

-- Thống kê theo giờ để vẽ biểu đồ thời gian trên web
hourly_clicks = FOREACH clicks GENERATE
    SUBSTRING(click_time, 0, 13) AS click_hour,
    is_attributed;

by_hour = GROUP hourly_clicks BY click_hour;

hourly_stats = FOREACH by_hour GENERATE
    group AS click_hour,
    COUNT(hourly_clicks) AS click_count,
    SUM(hourly_clicks.is_attributed) AS conversions;

STORE ip_risk INTO 'output/real_ip_risk'
    USING PigStorage(',');

STORE hourly_stats INTO 'output/hourly_stats'
    USING PigStorage(',');

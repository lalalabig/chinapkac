-- 修复 reports_reportdownloadlog 表
CREATE TABLE IF NOT EXISTS reports_reportdownloadlog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    download_time DATETIME NOT NULL,
    ip_address VARCHAR(39) NULL,
    downloader_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    report_id INTEGER NOT NULL REFERENCES reports_report(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_reportdownloadlog_report_id ON reports_reportdownloadlog(report_id);
CREATE INDEX IF NOT EXISTS idx_reportdownloadlog_downloader_id ON reports_reportdownloadlog(downloader_id);
CREATE INDEX IF NOT EXISTS idx_reportdownloadlog_download_time ON reports_reportdownloadlog(download_time);

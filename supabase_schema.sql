-- QR Code Reader Premium Platform Database Schema
-- Run this in your Supabase SQL Editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    tier VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- QR Scans table
CREATE TABLE qr_scans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    filename VARCHAR(255),
    file_size INTEGER,
    scan_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Analytics metadata
    ip_address VARCHAR(45),
    user_agent TEXT,
    referer VARCHAR(500),
    country VARCHAR(2),
    device_type VARCHAR(50),
    browser VARCHAR(100)
);

-- QR Codes table
CREATE TABLE qr_codes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    short_url VARCHAR(100) UNIQUE,
    destination_url TEXT NOT NULL,
    title VARCHAR(255),
    description TEXT,
    
    -- QR Code properties
    error_correction_level VARCHAR(10) DEFAULT 'M',
    size INTEGER DEFAULT 10,
    border INTEGER DEFAULT 4,
    
    -- Customization
    foreground_color VARCHAR(7) DEFAULT '#000000',
    background_color VARCHAR(7) DEFAULT '#FFFFFF',
    logo_url VARCHAR(500),
    
    -- Analytics
    scan_count INTEGER DEFAULT 0,
    last_scanned_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true
);

-- Subscriptions table
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    stripe_customer_id VARCHAR(255) UNIQUE,
    stripe_subscription_id VARCHAR(255) UNIQUE,
    tier VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    
    -- Billing
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    cancel_at_period_end BOOLEAN DEFAULT false,
    
    -- Usage tracking
    monthly_scan_limit INTEGER NOT NULL,
    scans_used_this_month INTEGER DEFAULT 0,
    last_reset_date TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API Keys table
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    rate_limit_per_minute INTEGER DEFAULT 60,
    rate_limit_per_hour INTEGER DEFAULT 1000,
    
    -- Usage tracking
    requests_this_minute INTEGER DEFAULT 0,
    requests_this_hour INTEGER DEFAULT 0,
    last_request_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true
);

-- QR Code Analytics table
CREATE TABLE qr_code_analytics (
    id SERIAL PRIMARY KEY,
    qr_code_id INTEGER REFERENCES qr_codes(id) ON DELETE CASCADE NOT NULL,
    scan_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Location data
    ip_address VARCHAR(45),
    country VARCHAR(2),
    region VARCHAR(100),
    city VARCHAR(100),
    
    -- Device and browser info
    user_agent TEXT,
    device_type VARCHAR(50),
    browser VARCHAR(100),
    os VARCHAR(100),
    
    -- Referral data
    referer VARCHAR(500),
    utm_source VARCHAR(100),
    utm_medium VARCHAR(100),
    utm_campaign VARCHAR(100),
    
    -- Additional metadata
    scan_metadata JSONB
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_qr_scans_user_id ON qr_scans(user_id);
CREATE INDEX idx_qr_scans_timestamp ON qr_scans(scan_timestamp);
CREATE INDEX idx_qr_codes_user_id ON qr_codes(user_id);
CREATE INDEX idx_qr_codes_short_url ON qr_codes(short_url);
CREATE INDEX idx_qr_codes_created_at ON qr_codes(created_at);
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);
CREATE INDEX idx_qr_analytics_qr_code_id ON qr_code_analytics(qr_code_id);
CREATE INDEX idx_qr_analytics_timestamp ON qr_code_analytics(scan_timestamp);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_qr_codes_updated_at BEFORE UPDATE ON qr_codes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_api_keys_updated_at BEFORE UPDATE ON api_keys FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample data (optional)
INSERT INTO users (email, password_hash, tier) VALUES 
('admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8QZqK2', 'enterprise');

-- Enable Row Level Security (RLS) for multi-tenant security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE qr_codes ENABLE ROW LEVEL SECURITY;
ALTER TABLE qr_scans ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE qr_code_analytics ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (basic - you can customize these)
CREATE POLICY "Users can view own data" ON users FOR SELECT USING (auth.uid()::text = id::text);
CREATE POLICY "Users can update own data" ON users FOR UPDATE USING (auth.uid()::text = id::text);

CREATE POLICY "Users can view own QR codes" ON qr_codes FOR SELECT USING (auth.uid()::text = user_id::text);
CREATE POLICY "Users can insert own QR codes" ON qr_codes FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);
CREATE POLICY "Users can update own QR codes" ON qr_codes FOR UPDATE USING (auth.uid()::text = user_id::text);
CREATE POLICY "Users can delete own QR codes" ON qr_codes FOR DELETE USING (auth.uid()::text = user_id::text);

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;

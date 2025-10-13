import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || 'https://rmzozjbdslkdvxtrmsue.supabase.co'
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJtem96amJkc2xrZHZ4dHJtc3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjAyOTg4NjYsImV4cCI6MjA3NTg3NDg2Nn0.9K2cKigG1rmEpG-A8QU88ywZObflIAz5lTevPi7Ff2w'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Auth functions
export const authAPI = {
  signUp: async (email, password) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
    })
    return { data, error }
  },
  
  signIn: async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    return { data, error }
  },
  
  signOut: async () => {
    const { error } = await supabase.auth.signOut()
    return { error }
  },
  
  getCurrentUser: async () => {
    const { data: { user }, error } = await supabase.auth.getUser()
    return { user, error }
  },
  
  resetPassword: async (email) => {
    const { data, error } = await supabase.auth.resetPasswordForEmail(email)
    return { data, error }
  }
}

// QR Code functions
export const qrAPI = {
  // Get user's QR codes
  getQRCodes: async () => {
    const { data, error } = await supabase
      .from('qr_codes')
      .select('*')
      .order('created_at', { ascending: false })
    return { data, error }
  },
  
  // Create new QR code
  createQRCode: async (qrData) => {
    const { data, error } = await supabase
      .from('qr_codes')
      .insert([qrData])
      .select()
    return { data, error }
  },
  
  // Update QR code
  updateQRCode: async (id, updates) => {
    const { data, error } = await supabase
      .from('qr_codes')
      .update(updates)
      .eq('id', id)
      .select()
    return { data, error }
  },
  
  // Delete QR code
  deleteQRCode: async (id) => {
    const { data, error } = await supabase
      .from('qr_codes')
      .delete()
      .eq('id', id)
    return { data, error }
  },
  
  // Get QR code analytics
  getQRAnalytics: async (qrCodeId) => {
    const { data, error } = await supabase
      .from('qr_code_analytics')
      .select('*')
      .eq('qr_code_id', qrCodeId)
      .order('scan_timestamp', { ascending: false })
    return { data, error }
  }
}

// Analytics functions
export const analyticsAPI = {
  getDashboardStats: async () => {
    const { data: qrCodes, error: qrError } = await supabase
      .from('qr_codes')
      .select('id, scan_count')
    
    const { data: scans, error: scanError } = await supabase
      .from('qr_scans')
      .select('scan_timestamp')
      .gte('scan_timestamp', new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString())
    
    if (qrError || scanError) {
      return { data: null, error: qrError || scanError }
    }
    
    const totalScans = qrCodes?.reduce((sum, qr) => sum + (qr.scan_count || 0), 0) || 0
    const recentScans = scans?.length || 0
    
    return {
      data: {
        total_qr_codes: qrCodes?.length || 0,
        total_scans: totalScans,
        recent_scans: recentScans
      },
      error: null
    }
  }
}

// File upload functions
export const storageAPI = {
  uploadFile: async (file, bucket = 'uploads') => {
    const fileName = `${Date.now()}-${file.name}`
    const { data, error } = await supabase.storage
      .from(bucket)
      .upload(fileName, file)
    return { data, error }
  },
  
  getFileUrl: (fileName, bucket = 'uploads') => {
    const { data } = supabase.storage
      .from(bucket)
      .getPublicUrl(fileName)
    return data.publicUrl
  }
}

export default supabase

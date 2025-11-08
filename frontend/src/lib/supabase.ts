import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://vkinrbcqzvcellsmaciy.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZraW5yYmNxenZjZWxsc21hY2l5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA4OTg1MzAsImV4cCI6MjA3NjQ3NDUzMH0.zdfDwI9fv3sgNkSsyUoq-eZI7mt1wkO-gr6S8Sbq8BI';

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

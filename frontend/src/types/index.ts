export interface User {
  id: string;
  username: string;
  email?: string;
}

export interface ScanResult {
  id: string;
  url: string;
  status: 'safe' | 'medium' | 'high';
  threatLevel: 'Safe' | 'Medium' | 'High';
  notes: string;
  timestamp: string;
  isOnion?: boolean;
}

export interface AIQuery {
  id: string;
  query: string;
  answer: string;
  timestamp: string;
}

export interface DashboardStats {
  totalScans: number;
  highThreat: number;
  mediumThreat: number;
  safeThreat: number;
}

export interface Settings {
  theme: 'dark' | 'light';
  torEnabled: boolean;
  apiKey: string;
}

import { create } from 'zustand';

export interface HistoryItem {
  step: number;
  tool: string;
  success: boolean;
  reasoning: string;
  message: string;
  verification?: string;
}

interface AutomationState {
  sessionId: string | null;
  status: 'idle' | 'running' | 'completed' | 'error' | 'stopped' | 'waiting_for_input';
  currentStep: number;
  currentUrl: string;
  currentAction: string;
  screenshotUrl: string | null;
  history: HistoryItem[];
  goal: string;
  validationErrors: string[] | null;
  
  setSessionId: (id: string | null) => void;
  setStatus: (status: 'idle' | 'running' | 'completed' | 'error' | 'stopped' | 'waiting_for_input') => void;
  setGoal: (goal: string) => void;
  setValidationErrors: (errors: string[] | null) => void;
  updateFromSocket: (data: Partial<AutomationState>) => void;
  reset: () => void;
}

export const useAutomationStore = create<AutomationState>((set) => ({
  sessionId: null,
  status: 'idle',
  currentStep: 0,
  currentUrl: '',
  currentAction: '',
  screenshotUrl: null,
  history: [],
  goal: '',
  validationErrors: null,

  setSessionId: (id) => set({ sessionId: id }),
  setStatus: (status) => set({ status }),
  setGoal: (goal) => set({ goal }),
  setValidationErrors: (errors) => set({ validationErrors: errors }),
  updateFromSocket: (data) => set((state) => ({
    ...state,
    ...data
  })),
  reset: () => set({
    sessionId: null,
    status: 'idle',
    currentStep: 0,
    currentUrl: '',
    currentAction: '',
    screenshotUrl: null,
    history: [],
    validationErrors: null
  })
}));

import { createSlice, PayloadAction } from '@reduxjs/toolkit';

// Simple types
interface Question {
  id: number;
  title: string;
  difficulty: string;
}

interface QuestionsState {
  questions: Question[];
  loading: boolean;
  error: string | null;
}

const initialState: QuestionsState = {
  questions: [],
  loading: false,
  error: null,
};

const questionsSlice = createSlice({
  name: 'questions',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setQuestions: (state, action: PayloadAction<Question[]>) => {
      state.questions = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
  },
});

export const { setLoading, setQuestions, setError } = questionsSlice.actions;
export default questionsSlice.reducer;

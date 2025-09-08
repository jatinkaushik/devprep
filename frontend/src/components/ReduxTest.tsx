import React from 'react';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { setLoading } from '../store/slices/simpleQuestionsSlice';

export const ReduxTest: React.FC = () => {
  const dispatch = useAppDispatch();
  const { loading, questions } = useAppSelector(state => state.questions);

  return (
    <div className="p-4 bg-green-50 border border-green-200 rounded-lg mb-4">
      <h3 className="text-green-800 font-medium mb-2">🎉 Redux Working!</h3>
      <p className="text-green-600 mb-2">
        Loading state: <span className="font-mono">{loading.toString()}</span>
      </p>
      <p className="text-green-600 mb-2">
        Questions count: <span className="font-mono">{questions.length}</span>
      </p>
      <button
        onClick={() => dispatch(setLoading(!loading))}
        className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
      >
        Toggle Loading
      </button>
    </div>
  );
};

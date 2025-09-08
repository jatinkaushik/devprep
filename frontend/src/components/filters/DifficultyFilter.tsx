import React from 'react';
import { getDifficultyBadgeClass } from '../../utils';
import { X } from 'lucide-react';

interface DifficultyFilterProps {
  difficulties: string[];
  selectedDifficulties: string[];
  onChange: (difficulties: string[]) => void;
}

export const DifficultyFilter: React.FC<DifficultyFilterProps> = ({
  difficulties,
  selectedDifficulties,
  onChange,
}) => {
  const handleToggle = (difficulty: string) => {
    if (selectedDifficulties.includes(difficulty)) {
      onChange(selectedDifficulties.filter(d => d !== difficulty));
    } else {
      onChange([...selectedDifficulties, difficulty]);
    }
  };

  const clearSelection = () => {
    onChange([]);
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Difficulty
        </label>
        {selectedDifficulties.length > 0 && (
          <button
            onClick={clearSelection}
            className="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 flex items-center gap-1 transition-colors"
          >
            <X size={12} />
            Clear
          </button>
        )}
      </div>
      
      <div className="flex flex-wrap gap-2">
        {difficulties.map(difficulty => (
          <button
            key={difficulty}
            onClick={() => handleToggle(difficulty)}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-all ${
              selectedDifficulties.includes(difficulty)
                ? getDifficultyBadgeClass(difficulty)
                : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            {difficulty}
          </button>
        ))}
      </div>
      
      {selectedDifficulties.length > 0 && (
        <div className="text-xs text-gray-500 dark:text-gray-400">
          {selectedDifficulties.length} difficulty level{selectedDifficulties.length !== 1 ? 's' : ''} selected
        </div>
      )}
    </div>
  );
};

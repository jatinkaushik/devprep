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
        <label className="block text-sm font-medium text-gray-700">
          Difficulty
        </label>
        {selectedDifficulties.length > 0 && (
          <button
            onClick={clearSelection}
            className="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
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
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {difficulty}
          </button>
        ))}
      </div>
      
      {selectedDifficulties.length > 0 && (
        <div className="text-xs text-gray-500">
          {selectedDifficulties.length} difficulty level{selectedDifficulties.length !== 1 ? 's' : ''} selected
        </div>
      )}
    </div>
  );
};

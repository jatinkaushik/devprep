import React from 'react';
import { TIME_PERIOD_LABELS } from '../../types';
import { X } from 'lucide-react';

interface TimePeriodFilterProps {
  timePeriods: string[];
  selectedTimePeriods: string[];
  onChange: (timePeriods: string[]) => void;
}

export const TimePeriodFilter: React.FC<TimePeriodFilterProps> = ({
  timePeriods,
  selectedTimePeriods,
  onChange,
}) => {
  const handleToggle = (timePeriod: string) => {
    if (selectedTimePeriods.includes(timePeriod)) {
      onChange(selectedTimePeriods.filter(tp => tp !== timePeriod));
    } else {
      onChange([...selectedTimePeriods, timePeriod]);
    }
  };

  const clearSelection = () => {
    onChange([]);
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-700">
          Time Period
        </label>
        {selectedTimePeriods.length > 0 && (
          <button
            onClick={clearSelection}
            className="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
          >
            <X size={12} />
            Clear
          </button>
        )}
      </div>
      
      <div className="space-y-1">
        {timePeriods.map(timePeriod => (
          <label key={timePeriod} className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={selectedTimePeriods.includes(timePeriod)}
              onChange={() => handleToggle(timePeriod)}
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm text-gray-700">
              {TIME_PERIOD_LABELS[timePeriod] || timePeriod}
            </span>
          </label>
        ))}
      </div>
      
      {selectedTimePeriods.length > 0 && (
        <div className="text-xs text-gray-500">
          {selectedTimePeriods.length} time period{selectedTimePeriods.length !== 1 ? 's' : ''} selected
        </div>
      )}
    </div>
  );
};

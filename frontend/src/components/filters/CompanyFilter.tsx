import React from 'react';
import { Company } from '../../types';
import Select from 'react-select';
import { X } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';

interface CompanyFilterProps {
  companies: Company[];
  selectedCompanies: string[];
  onChange: (companies: string[]) => void;
  isLoading?: boolean;
}

export const CompanyFilter: React.FC<CompanyFilterProps> = ({
  companies,
  selectedCompanies,
  onChange,
  isLoading = false,
}) => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  
  const options = companies.map(company => ({
    value: company.name,
    label: company.name,
  }));

  const selectedOptions = options.filter(option => 
    selectedCompanies.includes(option.value)
  );

  const handleChange = (selected: any) => {
    const values = selected ? selected.map((option: any) => option.value) : [];
    onChange(values);
  };

  const clearSelection = () => {
    onChange([]);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Companies
        </label>
        {selectedCompanies.length > 0 && (
          <button
            onClick={clearSelection}
            className="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 flex items-center gap-1 transition-colors"
          >
            <X size={12} />
            Clear
          </button>
        )}
      </div>
      
      <Select
        isMulti
        value={selectedOptions}
        onChange={handleChange}
        options={options}
        isLoading={isLoading}
        placeholder="Select companies..."
        className="text-sm"
        classNamePrefix="react-select"
        styles={{
          control: (base, state) => ({
            ...base,
            backgroundColor: isDark ? '#374151' : 'white',
            borderColor: state.isFocused 
              ? '#6366f1'
              : (isDark ? '#6b7280' : '#d1d5db'),
            boxShadow: state.isFocused ? '0 0 0 1px #6366f1' : 'none',
            color: isDark ? '#f9fafb' : '#374151',
            '&:hover': {
              borderColor: state.isFocused 
                ? '#6366f1' 
                : '#9ca3af',
            },
          }),
          menu: (base) => ({
            ...base,
            backgroundColor: isDark ? '#374151' : 'white',
            border: isDark ? '1px solid #6b7280' : '1px solid #d1d5db',
          }),
          option: (base, state) => ({
            ...base,
            backgroundColor: state.isSelected 
              ? '#6366f1' 
              : state.isFocused 
                ? (isDark ? '#4b5563' : '#f3f4f6')
                : 'transparent',
            color: state.isSelected 
              ? 'white' 
              : (isDark ? '#f9fafb' : '#374151'),
          }),
          multiValue: (base) => ({
            ...base,
            backgroundColor: isDark ? '#4b5563' : '#e5e7eb',
          }),
          multiValueLabel: (base) => ({
            ...base,
            color: isDark ? '#f9fafb' : '#374151',
          }),
          multiValueRemove: (base) => ({
            ...base,
            color: isDark ? '#9ca3af' : '#6b7280',
            '&:hover': {
              backgroundColor: isDark ? '#374151' : '#f3f4f6',
              color: isDark ? '#f9fafb' : '#374151',
            },
          }),
          input: (base) => ({
            ...base,
            color: isDark ? '#f9fafb' : '#374151',
          }),
          placeholder: (base) => ({
            ...base,
            color: isDark ? '#6b7280' : '#9ca3af',
          }),
          singleValue: (base) => ({
            ...base,
            color: isDark ? '#f9fafb' : '#374151',
          }),
        }}
      />
      
      {selectedCompanies.length > 0 && (
        <div className="text-xs text-gray-500 dark:text-gray-400">
          {selectedCompanies.length} company{selectedCompanies.length !== 1 ? 'ies' : ''} selected
        </div>
      )}
    </div>
  );
};

import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatAcceptanceRate(rate?: number): string {
  if (rate === undefined || rate === null) return 'N/A';
  return `${(rate * 100).toFixed(1)}%`;
}

export function formatFrequency(frequency?: number): string {
  if (frequency === undefined || frequency === null) return 'N/A';
  return frequency.toFixed(1);
}

export function getDifficultyColor(difficulty: string): string {
  switch (difficulty.toUpperCase()) {
    case 'EASY':
      return 'text-green-600';
    case 'MEDIUM':
      return 'text-yellow-600';
    case 'HARD':
      return 'text-red-600';
    default:
      return 'text-gray-600';
  }
}

export function getDifficultyBadgeClass(difficulty: string): string {
  switch (difficulty.toUpperCase()) {
    case 'EASY':
      return 'bg-green-100 text-green-800';
    case 'MEDIUM':
      return 'bg-yellow-100 text-yellow-800';
    case 'HARD':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
}

export function parseTopics(topics?: string): string[] {
  if (!topics) return [];
  return topics.split(',').map(topic => topic.trim()).filter(Boolean);
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(this, args), delay);
  };
}

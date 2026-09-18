const PRIORITY_CONFIG = {
  HIGH: {
    emoji: '🔴',
    label: 'HIGH',
    style: 'bg-red-100 text-red-700 border border-red-300',
  },
  MEDIUM: {
    emoji: '🟠',
    label: 'MEDIUM',
    style: 'bg-orange-100 text-orange-700 border border-orange-300',
  },
  NORMAL: {
    emoji: '🟢',
    label: 'NORMAL',
    style: 'bg-green-100 text-green-700 border border-green-300',
  },
  REVIEW_REQUIRED: {
    emoji: '⚪',
    label: 'REVIEW',
    style: 'bg-gray-100 text-gray-600 border border-gray-300',
  },
};

const PriorityBadge = ({ priority }) => {
  const config = PRIORITY_CONFIG[priority] || PRIORITY_CONFIG.NORMAL;

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold ${config.style}`}>
      <span>{config.emoji}</span>
      <span>{config.label}</span>
    </span>
  );
};

export default PriorityBadge;
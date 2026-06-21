export function RupeeRadarIcon({ className = "w-9 h-9" }: { className?: string }) {
  return (
    <svg 
      className={className} 
      viewBox="0 0 100 100" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
    >
      <g stroke="currentColor">
        {/* Protruding Crosshairs */}
        <line x1="50" y1="2" x2="50" y2="98" strokeWidth="4" />
        <line x1="2" y1="50" x2="98" y2="50" strokeWidth="4" />
        
        {/* Diagonal Crosshairs */}
        <line x1="18" y1="18" x2="82" y2="82" strokeWidth="3" />
        <line x1="18" y1="82" x2="82" y2="18" strokeWidth="3" />
        
        {/* Radar Rings with gaps (dash array) */}
        <circle cx="50" cy="50" r="42" strokeWidth="5" strokeDasharray="30 8" />
        <circle cx="50" cy="50" r="28" strokeWidth="3" />
        
        {/* Connecting line to the dot */}
        <path d="M50 22 C60 22 66 26 70 30" strokeWidth="3" fill="none" />
        <circle cx="70" cy="30" r="5" fill="currentColor" stroke="none" />
      </g>
      
      {/* Center Cutout for Rupee */}
      <circle cx="50" cy="50" r="18" fill="var(--color-primary-container, #0f172a)" />
      <circle cx="50" cy="50" r="18" fill="currentColor" opacity="0.1" />
      
      {/* The Rupee Symbol */}
      <path
        d="M42 38h16M42 45h16M47 38c0 6 3 10 5 10v0M45 48l8 12"
        stroke="currentColor"
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

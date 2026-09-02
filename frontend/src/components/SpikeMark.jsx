// SpikeMark — the 4-spoke radial-spike glyph (Anthropic-style brand mark).
// Renders inline so it inherits the current text color.
import React from 'react'

export default function SpikeMark({ size = 20, color = 'currentColor', style }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      style={style}
      aria-hidden="true"
    >
      <g stroke={color} strokeWidth="1.9" strokeLinecap="round">
        <line x1="12" y1="2" x2="12" y2="22" />
        <line x1="3" y1="8" x2="21" y2="16" />
        <line x1="3" y1="16" x2="21" y2="8" />
      </g>
    </svg>
  )
}

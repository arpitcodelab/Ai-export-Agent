// Icons.jsx — small inline SVG icon set for the chat panel, in the same
// style as SpikeMark.jsx (stroke-based, currentColor, no external assets).
// Replaces emoji (which render inconsistently across OS/browsers/fonts)
// with crisp icons that inherit the surrounding text color and scale
// cleanly at any size.
import React from 'react'

const base = {
  fill: 'none',
  xmlns: 'http://www.w3.org/2000/svg',
  'aria-hidden': 'true',
}

export function IconHistory({ size = 16, color = 'currentColor' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base}>
      <g stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 12a9 9 0 1 0 3-6.7" />
        <path d="M3 4v5h5" />
        <path d="M12 7v5l3.5 2" />
      </g>
    </svg>
  )
}

export function IconPlus({ size = 16, color = 'currentColor' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base}>
      <g stroke={color} strokeWidth="1.8" strokeLinecap="round">
        <line x1="12" y1="5" x2="12" y2="19" />
        <line x1="5" y1="12" x2="19" y2="12" />
      </g>
    </svg>
  )
}

export function IconClose({ size = 18, color = 'currentColor' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base}>
      <g stroke={color} strokeWidth="1.8" strokeLinecap="round">
        <line x1="5" y1="5" x2="19" y2="19" />
        <line x1="19" y1="5" x2="5" y2="19" />
      </g>
    </svg>
  )
}

export function IconTrash({ size = 14, color = 'currentColor' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base}>
      <g stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M4 7h16" />
        <path d="M9 7V4h6v3" />
        <path d="M6 7l1 13h10l1-13" />
        <line x1="10" y1="11" x2="10" y2="17" />
        <line x1="14" y1="11" x2="14" y2="17" />
      </g>
    </svg>
  )
}

export function IconShip({ size = 20, color = 'currentColor' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base}>
      <g stroke={color} strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
        <path d="M4 15l1.5 5h13L20 15" />
        <path d="M6 15V6h9l3 5" />
        <line x1="9" y1="6" x2="9" y2="3" />
        <line x1="3" y1="15" x2="21" y2="15" />
      </g>
    </svg>
  )
}

export function IconUser({ size = 18, color = 'currentColor' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base}>
      <g stroke={color} strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="8" r="3.5" />
        <path d="M5 20c0-3.9 3.1-7 7-7s7 3.1 7 7" />
      </g>
    </svg>
  )
}

export function IconMic({ size = 17, color = 'currentColor' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base}>
      <g stroke={color} strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
        <rect x="9" y="3" width="6" height="11" rx="3" />
        <path d="M5 11a7 7 0 0 0 14 0" />
        <line x1="12" y1="18" x2="12" y2="21" />
        <line x1="9" y1="21" x2="15" y2="21" />
      </g>
    </svg>
  )
}

export function IconStop({ size = 17, color = 'currentColor' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base} fill={color}>
      <rect x="6" y="6" width="12" height="12" rx="2" />
    </svg>
  )
}

export function IconSpeaker({ size = 14, color = 'currentColor' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base}>
      <g stroke={color} strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
        <path d="M4 9v6h4l5 4V5L8 9H4z" />
        <path d="M16.5 8.5a5 5 0 0 1 0 7" />
      </g>
    </svg>
  )
}

export function IconPin({ size = 13, color = 'currentColor' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base}>
      <g stroke={color} strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z" />
        <circle cx="12" cy="10" r="2.3" />
      </g>
    </svg>
  )
}

export function IconPaperclip({ size = 13, color = 'currentColor' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base}>
      <path
        stroke={color}
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M8 12l6.5-6.5a3 3 0 1 1 4.2 4.2L10.5 18a5 5 0 1 1-7-7L12.5 2.7"
      />
    </svg>
  )
}

export function IconWarning({ size = 14, color = 'currentColor' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" {...base}>
      <g stroke={color} strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 3l10 18H2L12 3z" />
        <line x1="12" y1="10" x2="12" y2="14" />
        <circle cx="12" cy="17.3" r="0.15" fill={color} />
      </g>
    </svg>
  )
}

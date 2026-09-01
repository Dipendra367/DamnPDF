function Svg({ children, bg }) {
  return (
    <svg viewBox="0 0 48 48" width="48" height="48" aria-hidden="true">
      <rect width="48" height="48" rx="10" fill={bg} />
      {children}
    </svg>
  )
}

export function LogoMark({ size = 28 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden="true">
      <rect width="32" height="32" rx="7" fill="#E5322D" />
      <path
        d="M8 22V10h6.2c2.7 0 4.4 1.6 4.4 4s-1.7 4-4.4 4H11.2v4H8zm3.2-6.4h2.6c1.2 0 1.9-.7 1.9-1.7s-.7-1.6-1.9-1.6h-2.6v3.3z"
        fill="#fff"
      />
    </svg>
  )
}

export function ToolIcon({ name }) {
  switch (name) {
    case 'merge':
      return (
        <Svg bg="#FEECEC">
          <path d="M14 18h8v3l6-5.5-6-5.5v3h-8v5zm20 12h-8v-3l-6 5.5 6 5.5v-3h8v-5z" fill="#E5322D" />
        </Svg>
      )
    case 'split':
      return (
        <Svg bg="#FEECEC">
          <path d="M34 18h-8v3l-6-5.5 6-5.5v3h8v5zM14 30h8v-3l6 5.5-6 5.5v-3h-8v-5z" fill="#E5322D" />
        </Svg>
      )
    case 'compress':
      return (
        <Svg bg="#FEECEC">
          <path d="M16 14h16v4H16v-4zm2 8h12v4H18v-4zm2 8h8v4h-8v-4z" fill="#E5322D" />
        </Svg>
      )
    case 'pdfWord':
      return (
        <Svg bg="#E8F0FA">
          <path d="M14 12h12l8 8v16H14V12z" fill="#fff" stroke="#2B579A" strokeWidth="2" />
          <path d="M26 12v8h8" fill="none" stroke="#2B579A" strokeWidth="2" />
          <text x="24" y="34" textAnchor="middle" fontSize="9" fontWeight="800" fill="#2B579A">W</text>
        </Svg>
      )
    case 'pdfPpt':
      return (
        <Svg bg="#FBE9E4">
          <path d="M14 12h12l8 8v16H14V12z" fill="#fff" stroke="#D24726" strokeWidth="2" />
          <path d="M26 12v8h8" fill="none" stroke="#D24726" strokeWidth="2" />
          <text x="24" y="34" textAnchor="middle" fontSize="9" fontWeight="800" fill="#D24726">P</text>
        </Svg>
      )
    case 'pdfExcel':
      return (
        <Svg bg="#E6F4EA">
          <path d="M14 12h12l8 8v16H14V12z" fill="#fff" stroke="#217346" strokeWidth="2" />
          <path d="M26 12v8h8" fill="none" stroke="#217346" strokeWidth="2" />
          <text x="24" y="34" textAnchor="middle" fontSize="9" fontWeight="800" fill="#217346">X</text>
        </Svg>
      )
    case 'wordPdf':
      return (
        <Svg bg="#E8F0FA">
          <rect x="12" y="14" width="24" height="20" rx="3" fill="#2B579A" />
          <text x="24" y="28" textAnchor="middle" fontSize="10" fontWeight="800" fill="#fff">DOC</text>
        </Svg>
      )
    case 'pptPdf':
      return (
        <Svg bg="#FBE9E4">
          <rect x="12" y="14" width="24" height="20" rx="3" fill="#D24726" />
          <text x="24" y="28" textAnchor="middle" fontSize="10" fontWeight="800" fill="#fff">PPT</text>
        </Svg>
      )
    case 'excelPdf':
      return (
        <Svg bg="#E6F4EA">
          <rect x="12" y="14" width="24" height="20" rx="3" fill="#217346" />
          <text x="24" y="28" textAnchor="middle" fontSize="10" fontWeight="800" fill="#fff">XLS</text>
        </Svg>
      )
    case 'pdfJpg':
      return (
        <Svg bg="#FFF6E5">
          <rect x="13" y="15" width="22" height="18" rx="2" fill="#fff" stroke="#F5A623" strokeWidth="2" />
          <circle cx="19" cy="22" r="2" fill="#F5A623" />
          <path d="M16 30l6-7 5 5 3-3 4 5H16z" fill="#F5A623" />
        </Svg>
      )
    case 'jpgPdf':
      return (
        <Svg bg="#FFF6E5">
          <rect x="14" y="12" width="20" height="24" rx="2" fill="#fff" stroke="#E5322D" strokeWidth="2" />
          <text x="24" y="28" textAnchor="middle" fontSize="8" fontWeight="800" fill="#E5322D">PDF</text>
        </Svg>
      )
    default:
      return (
        <Svg bg="#FEECEC">
          <text x="24" y="28" textAnchor="middle" fontSize="10" fontWeight="800" fill="#E5322D">PDF</text>
        </Svg>
      )
  }
}

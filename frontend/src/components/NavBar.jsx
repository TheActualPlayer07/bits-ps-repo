const PAR = 'PAR'
const SAGE = 'SAGE'

function renderLetters(text, color, delayOffset) {
  return text.split('').map((letter, index) => (
    <span
      key={index}
      className="navbar__letter"
      style={{
        color: color,
        animationDelay: `${(index + delayOffset) * 0.15}s`,
      }}
    >
      {letter}
    </span>
  ))
}

export default function Navbar() {
  return (
    <header className="navbar">
      <span className="navbar__brand">
        {renderLetters(PAR, '#d40000', 0)}
        {renderLetters(SAGE, '#1a4fd4', 3)}
      </span>
    </header>
  )
}
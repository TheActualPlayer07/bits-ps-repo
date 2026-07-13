import { useEffect, useRef, useState } from 'react';

export default function IntroSketch({ onEnter }) {
  const rootRef = useRef(null);
  const sketchRef = useRef(null);
  const [revealed, setRevealed] = useState(false);
  const [hiding, setHiding] = useState(false);

  useEffect(() => {
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const paths = sketchRef.current.querySelectorAll('path');

    let delay = 0;
    paths.forEach((p) => {
      const len = p.getTotalLength();
      p.style.strokeDasharray = len;
      p.style.strokeDashoffset = len;
      if (reduced) {
        p.style.strokeDashoffset = 0;
        return;
      }
      p.style.transition = `stroke-dashoffset ${(0.5 + len / 900).toFixed(2)}s ease ${delay.toFixed(2)}s`;
      requestAnimationFrame(() => requestAnimationFrame(() => (p.style.strokeDashoffset = 0)));
      delay += 0.09;
    });

    const totalDelay = reduced ? 0 : delay + 0.6;
    const t = setTimeout(() => setRevealed(true), totalDelay * 1000);
    return () => clearTimeout(t);
  }, []);

  function handleEnter() {
    setHiding(true);
    setTimeout(onEnter, 250);
  }

  return (
    <div className="rc-root" ref={rootRef}>
      <section className={`rc-intro${hiding ? ' rc-hide' : ''}${revealed ? ' rc-revealed' : ''}`}>
        <div className="rc-sketch-wrap">
          <svg className="rc-sketch" ref={sketchRef} viewBox="0 0 600 420" xmlns="http://www.w3.org/2000/svg">
            <path d="M90 360 L90 90 M90 90 L75 90 M90 90 L105 90" />
            <path d="M510 360 L510 90 M510 90 L495 90 M510 90 L525 90" />
            <path d="M75 360 L525 360" />
            <path d="M70 90 L300 30 L530 90" />
            <path d="M110 90 L300 45 L490 90" />
            <path d="M180 360 L180 300 L420 300 L420 360" />
            <path d="M195 300 L195 270 M420 300 L420 270" />
            <path d="M170 300 L430 300" />
            <path d="M300 300 L300 150" />
            <path d="M270 150 L330 150" />
            <path d="M300 150 L300 130" />
            <path className="rc-accent" d="M230 155 L300 140 L370 155" />
            <path className="rc-accent" d="M210 155 Q230 190 250 155" />
            <path className="rc-accent" d="M350 155 Q370 190 390 155" />
            <path d="M230 155 L230 155 M230 155 Q230 145 230 155" />
            <path d="M210 155 L250 155 M350 155 L390 155" />
            <path d="M110 260 L155 225" />
            <path d="M130 215 L172 245" />
            <path d="M100 270 L130 250" />
            <path className="rc-hatch" d="M185 355 L200 340 M195 355 L210 340 M205 355 L220 340 M215 355 L230 340" />
            <path className="rc-hatch" d="M390 355 L405 340 M400 355 L415 340 M410 355 L425 340" />
          </svg>
        </div>
        <div className="rc-eyebrow">Life Choices, Cross-Examined</div>
        <h1 className="rc-title">AI Judge</h1>
        <p className="rc-sub">
          Put a real decision on trial. Prosecutor and defence argue it out over several rounds, a judge
          scores it, and you walk away with a verdict and a full transcript.
        </p>
        <button className="rc-enter" onClick={handleEnter}>
          Enter the Courtroom →
        </button>
      </section>
    </div>
  );
}

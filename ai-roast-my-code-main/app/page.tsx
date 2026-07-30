import ReviewApp from "@/components/ReviewApp";

export default function Home() {
  return (
    <main className="min-h-screen">
      <div className="mx-auto max-w-3xl px-6 pb-28 pt-16 sm:pt-24">
        <header className="mb-14">
          <div className="mb-5 flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-ink-dim">
            <span className="h-1.5 w-1.5 rounded-full bg-ember" />
            order up
          </div>
          <h1 className="font-display text-4xl italic leading-tight text-ink sm:text-5xl">
            Send your code to the pass.
          </h1>
          <p className="mt-5 max-w-xl text-[15px] leading-relaxed text-ink-dim">
            One kitchen, two chefs, one ticket. Vex and Sage read the exact same scores and
            findings — they just plate it differently. Paste code, pick a language, and see what
            comes back.
          </p>
        </header>
        <ReviewApp />
      </div>
    </main>
  );
}

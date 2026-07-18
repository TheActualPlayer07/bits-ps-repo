export default function StatusBanner({ status, message }) {
  if (!status) return null

  return (
    <div className={`status-banner status-banner--${status}`}>
      {message}
    </div>
  )
}
// components/Spinner.jsx
export default function Spinner({ size = 4 }) {
  return (
    <span
      className={`inline-block h-${size} w-${size} animate-spin rounded-full border-2 border-current border-t-transparent`}
    />
  );
}

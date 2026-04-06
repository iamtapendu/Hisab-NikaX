// components/Spinner.jsx

const sizeMap = {
  sm: "h-4 w-4",
  md: "h-6 w-6",
  lg: "h-8 w-8",
};
export default function Spinner({ size = "sm" }) {
  return (
    <span
      className={`inline-block ${sizeMap[size]} animate-spin rounded-full border-2 border-current border-t-transparent`}
    />
  );
}

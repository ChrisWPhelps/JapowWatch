export function fmt(n) { return n.toLocaleString("en"); }
export function fmtJPY(n) { return `¥${fmt(n)}`; }

export const statusColors = { open: "#e8c96a", partial: "#e8906a", closed: "#6a7aa8" };
export const statusLabels = { open: "Open", partial: "Partial", closed: "Closed" };
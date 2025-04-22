React.FC 是 React 中的类型定义，全称为 "React Function Component"（React 函数组件）。它是 TypeScript 与 React 结合使用时的一种类型声明方式。

主要特点：
1. 它是一个泛型类型，可以接受 props 的类型定义作为泛型参数
2. 它已经包含了 children 属性的类型定义
3. 它规定了组件的返回类型是 JSX.Element

在您的代码中：
```tsx
const InfoCard: React.FC<{
  title: string;
  index: number;
  desc: string;
  href: string;
}> = ({ title, href, index, desc }) => {
```

这段代码定义了一个名为 InfoCard 的函数组件，它接受四个 props：
- title: 字符串类型
- index: 数字类型
- desc: 字符串类型
- href: 字符串类型

使用 React.FC 有助于在开发过程中获得更好的类型检查和代码提示，特别是在处理组件 props 时。这是 TypeScript 与 React 结合使用的最佳实践之一。

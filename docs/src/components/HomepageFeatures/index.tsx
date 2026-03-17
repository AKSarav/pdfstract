import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  icon: ReactNode;
  description: ReactNode;
  link: string;
};

const ExtractIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
    <line x1="16" y1="13" x2="8" y2="13"/>
    <line x1="16" y1="17" x2="8" y2="17"/>
    <polyline points="10 9 9 9 8 9"/>
  </svg>
);

const ChunkIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="7" height="7" rx="1"/>
    <rect x="14" y="3" width="7" height="7" rx="1"/>
    <rect x="3" y="14" width="7" height="7" rx="1"/>
    <rect x="14" y="14" width="7" height="7" rx="1"/>
  </svg>
);

const EmbedIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="3"/>
    <path d="M12 2v4"/>
    <path d="M12 18v4"/>
    <path d="m4.93 4.93 2.83 2.83"/>
    <path d="m16.24 16.24 2.83 2.83"/>
    <path d="M2 12h4"/>
    <path d="M18 12h4"/>
    <path d="m4.93 19.07 2.83-2.83"/>
    <path d="m16.24 7.76 2.83-2.83"/>
  </svg>
);

const FeatureList: FeatureItem[] = [
  {
    title: 'Extract',
    icon: <ExtractIcon />,
    link: '/features/extract',
    description: (
      <>
        Convert PDFs with <strong>10+ libraries</strong> including Marker, Docling, 
        PyMuPDF4LLM, and more. Each optimized for different document types.
      </>
    ),
  },
  {
    title: 'Chunk',
    icon: <ChunkIcon />,
    link: '/features/chunk',
    description: (
      <>
        Split text with <strong>10+ methods</strong> from simple token-based 
        to advanced semantic chunking powered by AI.
      </>
    ),
  },
  {
    title: 'Embed',
    icon: <EmbedIcon />,
    link: '/features/embed',
    description: (
      <>
        Generate vector embeddings with <strong>multiple providers</strong> including 
        OpenAI, Sentence Transformers, and local models.
      </>
    ),
  },
];

function Feature({title, icon, description, link}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <Link to={link} className={styles.featureCard}>
        <div className={styles.featureIcon}>
          {icon}
        </div>
        <Heading as="h3" className={styles.featureTitle}>{title}</Heading>
        <p className={styles.featureDescription}>{description}</p>
      </Link>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className={styles.sectionHeader}>
          <Heading as="h2" className={styles.sectionTitle}>
            The Complete Data Preparation Pipeline
          </Heading>
          <p className={styles.sectionSubtitle}>
            Extract. Chunk. Embed. — From PDF to vector-ready in one command.
          </p>
        </div>
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
        
        <div className={styles.codeExample}>
          <p className={styles.valueProposition}>
            <strong>One unified API.</strong> Switch between libraries, chunkers, and embedding providers with a single parameter change.
          </p>
          <div className={styles.codeBlock}>
            <code>pdfstract convert-chunk-embed document.pdf --library auto --chunker auto --embedding auto</code>
          </div>
        </div>
      </div>
    </section>
  );
}

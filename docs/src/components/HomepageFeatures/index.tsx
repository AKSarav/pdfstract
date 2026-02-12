import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  image: string;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Extract',
    image: require('@site/static/img/extract.png').default,
    description: (
      <>
        Choose from Marker, Docling, PyMuPDF4LLM, Unstructured, PaddleOCR,
        and more. Each library optimized for different document types and quality needs.
      </>
    ),
  },
  {
    title: 'Chunk',
    image: require('@site/static/img/chunk.png').default,
    description: (
      <>
        Split text intelligently with 10+ chunking methods. From simple token-based
        to advanced <code>semantic chunking</code> powered by AI embeddings.
      </>
    ),
  },
  {
    title: 'Get your PDF ready for RAG',
    image: require('@site/static/img/ai-intel.png').default,
    description: (
      <>
        Get structured, chunked content ready for embedding models and vector databases.
        Perfect first layer for RAG applications and AI workflows.
      </>
    ),
  },
];

function Feature({title, image, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <img src={image} className={styles.featureSvg} alt={title} />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}

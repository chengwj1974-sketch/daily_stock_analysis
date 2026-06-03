import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import type { AnalysisReport } from '../../../types/analysis';
import { MarketReviewReportView } from '../MarketReviewReportView';

vi.mock('../../../api/history', () => ({
  historyApi: {
    getMarkdown: vi.fn(),
  },
}));

const englishMarketReviewReport: AnalysisReport = {
  meta: {
    queryId: 'market-review-q-1',
    stockCode: 'MARKET',
    stockName: 'Market Review',
    reportType: 'market_review',
    reportLanguage: 'en',
    createdAt: '2026-03-18T08:00:00Z',
  },
  summary: {
    analysisSummary: '',
    operationAdvice: '',
    trendPrediction: '',
    sentimentScore: undefined as unknown as number,
  },
};

describe('MarketReviewReportView', () => {
  it('uses localized summary card labels and fallbacks for English reports', () => {
    render(
      <MarketReviewReportView
        report={englishMarketReviewReport}
        content="# Market Review"
        reportLanguage="en"
      />,
    );

    expect(screen.getByText('Review Summary')).toBeInTheDocument();
    expect(screen.getByText('No review summary yet')).toBeInTheDocument();
    expect(screen.getByText('Market Sentiment')).toBeInTheDocument();
    expect(screen.getByText('No score yet')).toBeInTheDocument();
    expect(screen.getByText('Rotation & Funds')).toBeInTheDocument();
    expect(screen.getByText('No rotation view yet')).toBeInTheDocument();
    expect(screen.getByText('Risks & Watchlist')).toBeInTheDocument();
    expect(screen.getByText('No key observations yet')).toBeInTheDocument();
    expect(screen.queryByText('复盘摘要')).not.toBeInTheDocument();
    expect(screen.queryByText('暂无摘要')).not.toBeInTheDocument();
  });
});

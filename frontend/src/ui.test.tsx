import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, expect, test } from 'vitest'
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom'
import { ArticleCard, SearchBox } from './ui'

afterEach(cleanup)

test('search form preserves quoted Boolean expressions in the URL', () => {
  function Result() { return <p>{new URLSearchParams(useLocation().search).get('q')}</p> }
  render(<MemoryRouter><Routes><Route path="/" element={<SearchBox/>}/><Route path="/search" element={<Result/>}/></Routes></MemoryRouter>)
  fireEvent.change(screen.getByRole('textbox'), { target: { value: '("clinical trial" OR RCT) AND asthma' } })
  fireEvent.click(screen.getByRole('button', { name: 'Search' }))
  expect(screen.getByText('("clinical trial" OR RCT) AND asthma')).toBeTruthy()
})

test('article without DOI still links to its canonical PMID', () => {
  render(<MemoryRouter><ArticleCard article={{ pmid:'31452104', title:'Fixture article', authors:[], journal:'Fixture journal', year:'2019' }}/></MemoryRouter>)
  expect(screen.getByRole('link', { name:'Fixture article' }).getAttribute('href')).toBe('/article/31452104')
  expect(screen.queryByText(/DOI/)).toBeNull()
})
